import json
from datetime import date, datetime
from typing import Dict, List, NamedTuple, Tuple

import httpx
from bs4 import BeautifulSoup, Tag
from fastapi import HTTPException, status

from ... import __version__
from ...cache import Cache, NotInCache
from ...models.postcode import PostCode
from .models import RefuseCollection


class RefuseSession:
    API_BASEURL = "https://www1.arun.gov.uk/external"
    CACHE_NAMESPACE = "refuse_session"

    class FormData(NamedTuple):
        action: str
        method: str
        inputs: Dict[str, str]

    def __init__(
        self, session: httpx.AsyncClient, cache: Cache, postcode: PostCode
    ) -> None:
        self.session = session
        self.cache = cache
        self.postcode = postcode

    async def _do_request(
        self,
        method: str,
        url: str = None,
        path: str = None,
        expected_code: int = 200,
        **kwargs,
    ) -> BeautifulSoup:
        if path:
            url = f"{self.API_BASEURL}{path}"

        r = await self.session.request(method, url, **kwargs)
        if not r.status_code == expected_code:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Received {r.status_code} from upstream",
            )
        return BeautifulSoup(r.text, features="html.parser")

    async def _form_data_request(
        self,
        form_data: FormData,
        data: dict = None,
        del_data_keys: List[str] = [],
        **kwargs,
    ) -> BeautifulSoup:
        r_data = form_data["inputs"]
        if data:
            r_data.update(data)
        if del_data_keys:
            for item in del_data_keys:
                del r_data[item]
        r = await self._do_request(
            form_data["method"], url=form_data["action"], data=r_data, **kwargs
        )
        return r

    async def get(self, path: str, **kwargs) -> BeautifulSoup:
        return await self._do_request("get", path=path, **kwargs)

    async def post(self, path: str, **kwargs) -> BeautifulSoup:
        return await self._do_request("post", path=path, **kwargs)

    def _parse_form_from_page(
        self,
        soup: Tag,
        *args,
        prefix: str = None,
    ) -> dict:
        form: Tag = soup.find("form")
        res = {"method": form["method"], "action": form["action"], "inputs": {}}
        input: Tag
        for input in form.find_all("input"):
            try:
                if not prefix and not args:
                    res["inputs"][input["name"]] = input["value"]
                elif input["name"] in args:
                    res["inputs"][input["name"]] = input["value"]
                elif prefix and input["name"].startswith(prefix):
                    res["inputs"][input["name"]] = input["value"]
            except Exception:
                pass
        return res

    def parse_collection_info(self, lines: List[str]) -> RefuseCollection:
        data = {}
        for line in lines[1:]:
            words = line.strip().split(" ")
            if "are on a" in line:
                data["collection_day"] = words[-1].split(".")[0]
            if "rubbish" in line:
                data["next_rubbish"] = datetime.strptime(words[-1], "%d/%m/%Y")
            if "recycling" in line:
                data["next_recycling"] = datetime.strptime(words[-1], "%d/%m/%Y")
            if "food waste" in line:
                data["next_food_waste"] = datetime.strptime(words[-1], "%d/%m/%Y")
        return RefuseCollection(**data)

    async def get_results(self) -> Tuple[RefuseCollection, float]:
        CACHE_KEY = (f"next_collection.{self.postcode.postcode}", self.CACHE_NAMESPACE)
        try:
            cached, expiry = await self.cache.get_cache(*CACHE_KEY)
            return RefuseCollection(**json.loads(cached)), expiry
        except NotInCache:
            pass
        init_session = await self.get("/Cleansing_GDS_CollectionsSchedule.ofml")
        formdata = self._parse_form_from_page(init_session)
        post_resp = await self._form_data_request(formdata)
        search_form = self._parse_form_from_page(post_resp)
        postcode_search = await self._form_data_request(
            search_form, {"F_Postcodesearch": self.postcode.postcode}
        )
        selection = self._parse_form_from_page(postcode_search)
        try:
            results = await self._form_data_request(
                selection, {"BB_0": "1"}, del_data_keys=["BB_Cancel"]
            )
        except KeyError:
            raise
        collection_info = [
            x
            for x in results.find("div", {"class": "dlgmsg"}).contents
            if type(x) != Tag
        ]
        result = self.parse_collection_info(collection_info)
        soonest_end = min(
            result.next_recycling, result.next_rubbish, result.next_rubbish
        )
        ttl = datetime.fromordinal(soonest_end.toordinal()) - datetime.now()
        await self.cache.set_cache(result.json(), *CACHE_KEY, ttl=ttl)
        return result, ttl.seconds

    def cal_event_uid(self, date: date):
        from hashlib import sha256

        tohash = f"{date.isoformat()}{self.postcode.postcode}"
        encoded = tohash.encode("utf-8")
        hash = sha256(encoded).hexdigest()
        return hash

    async def get_calendar(self, baseurl: str, transparent: bool) -> str:
        from ics import Calendar, Event

        results, _ = await self.get_results()
        events = []
        evt_rubbish = Event(
            name="Rubbish Collection",
            begin=results.next_rubbish,
            uid=self.cal_event_uid(results.next_rubbish),
            transparent=transparent,
        )
        evt_rubbish.make_all_day()
        events.append(evt_rubbish)

        evt_recycling = Event(
            name="Recycling Collection",
            begin=results.next_recycling,
            uid=self.cal_event_uid(results.next_recycling),
            transparent=transparent,
        )
        evt_recycling.make_all_day()
        events.append(evt_recycling)

        if results.next_food_waste:
            evt_food_waste = Event(
                name="Food Waste Collection",
                begin=results.next_food_waste,
                uid=self.cal_event_uid(results.next_food_waste),
                transparent=transparent,
            )
            evt_food_waste.make_all_day()
            events.append(evt_food_waste)

        cal = Calendar(events=events, creator=f"arunapi_v{__version__} - {baseurl}")
        return str(cal)
