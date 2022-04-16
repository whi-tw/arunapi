from flask import Flask
from flask_restx import Resource, Api, fields

from . import binsapi

errors = {"InvalidPostcodeException": {"status": 400}}

app = Flask(__name__)
api = Api(app, errors=errors)


ns = api.namespace("refuse", description="Refuse collection")


@ns.route("/next_collection/<string:postcode>")
@ns.doc(params={"postcode": "A postcode with a space in the middle (BN17 5LF)"})
class NextCollectionForPostcode(Resource):
    model = api.model(
        "NextBinCollection",
        {
            "collection_day": fields.String(
                description="The day of the week this postcode's bins are collected"
            ),
            "next_rubbish": fields.Date(
                description="The date of the next rubbish collection"
            ),
            "next_recycling": fields.Date(
                description="The date of the next recycling collection"
            ),
        },
    )

    @api.marshal_with(model)
    def get(self, postcode: str):
        session = binsapi.BinsApiSession(postcode)
        results = session.get_results()
        return results
