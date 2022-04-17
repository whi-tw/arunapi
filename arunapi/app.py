from flask import Flask

from .api import blueprint as apiv1, API_VERSION

app = Flask(__name__)
app.register_blueprint(apiv1, url_prefix=f"/api/v{API_VERSION.major}")
