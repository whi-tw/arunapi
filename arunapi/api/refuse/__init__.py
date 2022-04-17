from flask_restx import Namespace, Resource, fields

from arunapi.cache import REDIS

from .session import RefuseSession

api = Namespace("Refuse", description="Refuse and Recycling")

next_bin_collection = api.model(
    "NextBinCollection",
    {
        "collection_day": fields.String(
            description="The day of the week this postcode's bins are collected",
            example="Monday",
        ),
        "next_rubbish": fields.Date(
            description="The date of the next rubbish collection"
        ),
        "next_recycling": fields.Date(
            description="The date of the next recycling collection"
        ),
        "next_food_waste": fields.Date(
            description="The date of the next food waste and absorbent hygiene products collection"
        ),
    },
)


@api.route("/next_collection/<string:postcode>")
@api.doc(params={"postcode": "A postcode with a space in the middle (BN17 5LF)"})
class NextCollectionForPostcode(Resource):
    @api.marshal_with(next_bin_collection)
    def get(self, postcode: str):
        session = RefuseSession(REDIS, postcode)
        results, cache_meta = session.get_results()
        return results, {
            "Cache-Control": f"max-age={cache_meta['ttl']}",
        }
