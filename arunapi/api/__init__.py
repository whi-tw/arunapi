from flask import Blueprint
from flask_restx import Api, Model, fields
import semver
from ._version import VERSION
from .refuse import api as refuse_api

API_VERSION = semver.VersionInfo.parse(VERSION)

blueprint = Blueprint("api", __name__)
api = Api(
    blueprint, version=VERSION, description="API for Arun District Council services"
)
api.add_namespace(refuse_api, path="/refuse")
