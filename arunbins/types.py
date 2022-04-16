from flask_restx import Model

from requests import Session


class BaseResponseClass:
    envelope = "result"


class ApiSession:
    API_BASEURL = "https://www1.arun.gov.uk/external"
    session: Session
    response_model: Model
