""" 
# ✅ Option 1: Basic Flask API (using Blueprint + Marshmallow)
from flask import Flask 
from .extensions import db, ma
from .routes.tickets import tickets_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    ma.init_app(app)

    app.register_blueprint(tickets_bp, url_prefix='/tickets')

    return app """


# ✅ Option 2: Flask-Smorest + Swagger + RESTful API
from flask import Flask
from app.extensions import db, ma
from flask_smorest import Api
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # Base configuration
    app.config.from_object("app.config.Config")

    # Swagger / OpenAPI config
    app.config["API_TITLE"] = "Smart Issue Tracker API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # Extensions
    db.init_app(app)
    ma.init_app(app)
    CORS(app)

    # Register the REST API using flask-smorest
    from app.routes.ticket_resource import blp as TicketBlueprint
    api = Api(app)
    api.register_blueprint(TicketBlueprint)

    return app
