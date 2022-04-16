from typing import Dict, List, NamedTuple
import requests

from datetime import datetime

from werkzeug.exceptions import InternalServerError, BadRequest

from bs4 import BeautifulSoup
from bs4.element import Tag

from ukpostcodeutils import validation

from .types import ApiSession


class InvalidPostcode(BadRequest):
    description = "Postcode is invalid"


class PostcodeMissingSpace(BadRequest):
    description = "Postcode must contain a space, ie. 'BN17 5LF' not 'BN175LF'"


class UnknownError(InternalServerError):
    description = "An unknown error occurred (possibly an incorrect postcode?)"


class FormData(NamedTuple):
    action: str
    method: str
    inputs: Dict[str, str]


class BinsApiSession(ApiSession):
    def __init__(self, postcode: str) -> None:
        self.session = requests.Session()
        self.postcode = self._validate_postcode(postcode)

    def _do_request(
        self, method: str, url: str = None, path: str = None, **kwargs
    ) -> BeautifulSoup:
        if path:
            url = f"{self.API_BASEURL}{path}"
        r = self.session.request(method, url, **kwargs)
        return BeautifulSoup(r.text, features="html.parser")

    def _form_data_request(
        self,
        form_data: FormData,
        data: dict = None,
        del_data_keys: List[str] = [],
        **kwargs,
    ) -> BeautifulSoup:
        r_data = form_data.inputs
        if data:
            r_data.update(data)
        if del_data_keys:
            for item in del_data_keys:
                del r_data[item]
        return self._do_request(
            form_data.method, url=form_data.action, data=r_data, **kwargs
        )

    def get(self, path: str, **kwargs) -> BeautifulSoup:
        return self._do_request("get", path=path, **kwargs)

    def post(self, path: str, **kwargs) -> BeautifulSoup:
        return self._do_request("post", path=path, **kwargs)

    def _parse_form_from_page(
        self,
        soup: Tag,
        *args,
        prefix: str = None,
    ):
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
            except:
                pass
        return FormData(**res)

    def parse_collection_info(self, lines: List[str]) -> dict:
        data = {}
        for line in lines[1:]:
            words = line.strip().split(" ")
            if "are on a" in line:
                data["collection_day"] = words[-1].split(".")[0]
            if "rubbish" in line:
                data["next_rubbish"] = datetime.strptime(words[-1], "%d/%m/%Y").date()
            if "recycling" in line:
                data["next_recycling"] = datetime.strptime(words[-1], "%d/%m/%Y").date()
        return data

    def get_results(self) -> FormData:
        init_session = self.get("/Cleansing_GDS_CollectionsSchedule.ofml")
        formdata = self._parse_form_from_page(init_session)
        post_resp = self._form_data_request(formdata)
        search_form = self._parse_form_from_page(post_resp)
        postcode_search = self._form_data_request(
            search_form, {"F_Postcodesearch": self.postcode}
        )
        selection = self._parse_form_from_page(postcode_search)
        try:
            results = self._form_data_request(
                selection, {"BB_0": "1"}, del_data_keys=["BB_Cancel"]
            )
        except KeyError:
            raise UnknownError
        collection_info = [
            x
            for x in results.find("div", {"class": "dlgmsg"}).contents
            if type(x) != Tag
        ]
        return self.parse_collection_info(collection_info)

    def _validate_postcode(self, postcode: str) -> str:
        postcode = postcode.upper().strip()
        if not validation.is_valid_postcode(postcode.replace(" ", "")):
            raise InvalidPostcode

        if " " not in postcode:
            raise PostcodeMissingSpace

        return postcode
