from fastapi import APIRouter, Query, Request, Response
from httpx import AsyncClient

from ...models.calendar import CalendarResponse
from ...models.postcode import PostCode
from .models import RefuseCollection
from .session import RefuseSession

router = APIRouter(prefix="/refuse", tags=["Refuse"])


@router.get("/next_collection/{postcode}", response_model=RefuseCollection)
async def get_next_collection(postcode: PostCode, request: Request, response: Response):
    async with AsyncClient() as session:
        s = RefuseSession(session, request.app.state.cache, postcode)
        data, expiry = await s.get_results()
        response.headers["X-Cache-Expires"] = str(expiry)
        return data


@router.get(
    "/next_collection/{postcode}/calendar",
    name="Calendar of next collections",
    response_class=CalendarResponse,
    responses={
        200: {
            "content": {
                CalendarResponse.media_type: {"example": CalendarResponse.example}
            },
            "description": "A calendar with the next available collections",
        },
    },
)
async def collection_calendar(
    postcode: PostCode,
    request: Request,
    transparent: bool = Query(
        True,
        description=(
            "Whether the events should be transparent "
            "(https://www.rfc-editor.org/rfc/rfc5545#section-3.8.2.7)"
        ),
    ),
):
    async with AsyncClient() as session:
        s = RefuseSession(session, request.app.state.cache, postcode)
        return await s.get_calendar(baseurl=request.base_url, transparent=transparent)
