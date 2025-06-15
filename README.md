# Learning Flask-API Fast with Senior-Level Structure
This tutorial explains 

- App structure (modular, scalable)
- Routing (Blueprints)
- Request handling (GET, POST, PUT, DELETE)
- Data validation (with Marshmallow or Pydantic)
- Database ORM (SQLAlchemy)
- Configs via .env (with python-dotenv)
- Error handling (custom exceptions)
- API docs (Swagger / OpenAPI via flasgger)
- Testing (Pytest + coverage)

## Create db
```
python init_db.py
```

## Run app
```
python run.py
```

## 1. Folder Structure
```
flask_api_project/
│
├── app/
│   ├── __init__.py         # App factory
│   ├── config.py           # Environment configs
│   ├── models/             # SQLAlchemy models
│   ├── routes/             # Routes
│   ├── schemas/            # Marshmallow schemas
│   ├── services/           # Business logic layer
│   ├── utils/              # Helpers
│   └── extensions.py       # DB, Marshmallow, JWT, etc.
│
├── migrations/             # Alembic migrations
├── tests/                  # Pytest-based tests
├── .env                    # Secrets & config
├── requirements.txt
├── run.py                  # Entry point
└── README.md
```

## 2. Requirements
```
pip install -r requirements.txt
python -m venv venv
venv\Scripts\activate 
```

## 3. Initialize Flask App
In app/__init__.py

### ✅ Option 1: Basic Flask API (using Blueprint + Marshmallow)
```
from flask import Flask 
from .extensions import db, ma
from .routes.tickets import tickets_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    ma.init_app(app)

    app.register_blueprint(tickets_bp, url_prefix='/tickets')

    return app
```

In app/__init__.py
### ✅ Option 2: Flask-Smorest + Swagger + RESTful API
```
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
```

In app/config.py
```
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///data.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

In app/extensions.py
```
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()
```

run.py
```
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

## 4. Ticket Model + Schema
In app/models/ticket.py

```
from app.extensions import db

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="open")
    priority = db.Column(db.String(50), default="medium")
```

In app/schemas/ticket.py

```
from app.extensions import ma
from app.models.ticket import Ticket

class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        load_instance = True
```

## 4. Ticket Routes (5 APIs)
In api/tickets.py

### Option 1: Basic Flask API (using Blueprint + Marshmallow)
```
from flask import Blueprint, request, jsonify, abort
from app.extensions import db
from app.models.ticket import Ticket
from app.schemas.ticket import TicketSchema

tickets_bp = Blueprint("tickets", __name__)
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)

# 1. Create Ticket
@tickets_bp.route('', methods=['POST'])
def create_ticket():
    data = request.get_json()
    ticket = ticket_schema.load(data)
    db.session.add(ticket)
    db.session.commit()
    return ticket_schema.jsonify(ticket), 201

# 2. Get All Tickets
@tickets_bp.route('', methods=['GET'])
def get_tickets():
    tickets = Ticket.query.all()
    return tickets_schema.jsonify(tickets)

# 3. Get Single Ticket
@tickets_bp.route('/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        abort(404, description="Ticket not found")
    return ticket_schema.jsonify(ticket)

# 4. Update Ticket
@tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        abort(404, description="Ticket not found")
    data = request.get_json()
    ticket.title = data.get("title", ticket.title)
    ticket.description = data.get("description", ticket.description)
    ticket.status = data.get("status", ticket.status)
    ticket.priority = data.get("priority", ticket.priority)
    db.session.commit()
    return ticket_schema.jsonify(ticket)

# 5. Delete Ticket
@tickets_bp.route('/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        abort(404, description="Ticket not found")
    db.session.delete(ticket)
    db.session.commit()
    return '', 204
```

In api/ticket_resource.py
### Option 2: Flask-Smorest + Swagger + RESTful API
```
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.extensions import db
from app.models.ticket import Ticket
from app.schemas.ticket import TicketSchema

blp = Blueprint("Tickets", "tickets", url_prefix="/tickets", description="Operations on tickets")

@blp.route("/")
class TicketList(MethodView):

    @blp.response(200, TicketSchema(many=True))
    def get(self):
        """Get all tickets"""
        return Ticket.query.all()

    @blp.arguments(TicketSchema)
    @blp.response(201, TicketSchema)
    def post(self, ticket):
        """Create a new ticket"""
        db.session.add(ticket)
        db.session.commit()
        return ticket


@blp.route("/<int:ticket_id>")
class TicketById(MethodView):

    @blp.response(200, TicketSchema)
    def get(self, ticket_id):
        """Get ticket by ID"""
        ticket = db.session.get(Ticket, ticket_id)
        if not ticket:
            abort(404, message="Ticket not found")
        return ticket

    @blp.arguments(TicketSchema(partial=True))
    @blp.response(200, TicketSchema)
    def put(self, updated_ticket, ticket_id):
        """Update a ticket by ID"""
        existing_ticket = db.session.get(Ticket, ticket_id)
        if not existing_ticket:
            abort(404, message="Ticket not found")

        # Update only provided fields
        for attr in ["title", "description", "status", "priority"]:
            value = getattr(updated_ticket, attr)
            if value is not None:
                setattr(existing_ticket, attr, value)

        db.session.commit()
        return existing_ticket

    def delete(self, ticket_id):
        """Delete a ticket by ID"""
        ticket = db.session.get(Ticket, ticket_id)
        if not ticket:
            abort(404, message="Ticket not found")
        db.session.delete(ticket)
        db.session.commit()
        return "", 204
```

## 5. Initialize DB
In init_db.py:
```
from app import create_app
from app.extensions import db
from app.models.ticket import Ticket  # Import all models to register them

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Database initialized.")
```

## 6. Swagger / OpenAPI Docs
```
pip install flask-smorest apispec[marshmallow] flask-cors
```

### 6.1. Create a new api/ticket_resource.py
In: app/api/ticket_resource.py
```
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.extensions import db
from app.models.ticket import Ticket
from app.schemas.ticket import TicketSchema

blp = Blueprint("Tickets", "tickets", url_prefix="/tickets", description="Operations on tickets")


@blp.route("/")
class TicketList(MethodView):

    @blp.response(200, TicketSchema(many=True))
    def get(self):
        """Get all tickets"""
        return Ticket.query.all()

    @blp.arguments(TicketSchema)
    @blp.response(201, TicketSchema)
    def post(self, ticket):
        """Create a new ticket"""
        db.session.add(ticket)
        db.session.commit()
        return ticket


@blp.route("/<int:ticket_id>")
class TicketById(MethodView):

    @blp.response(200, TicketSchema)
    def get(self, ticket_id):
        """Get ticket by ID"""
        ticket = db.session.get(Ticket, ticket_id)
        if not ticket:
            abort(404, message="Ticket not found")
        return ticket

    @blp.arguments(TicketSchema(partial=True))
    @blp.response(200, TicketSchema)
    def put(self, updated_ticket, ticket_id):
        """Update a ticket by ID"""
        existing_ticket = db.session.get(Ticket, ticket_id)
        if not existing_ticket:
            abort(404, message="Ticket not found")

        # Update only provided fields
        for attr in ["title", "description", "status", "priority"]:
            value = getattr(updated_ticket, attr)
            if value is not None:
                setattr(existing_ticket, attr, value)

        db.session.commit()
        return existing_ticket

    def delete(self, ticket_id):
        """Delete a ticket by ID"""
        ticket = db.session.get(Ticket, ticket_id)
        if not ticket:
            abort(404, message="Ticket not found")
        db.session.delete(ticket)
        db.session.commit()
        return "", 204
```

### 6.2. Update your create_app to register docs and blueprints
In app/__init__.py:
```
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
    from app.api.ticket_resource import blp as TicketBlueprint
    api = Api(app)
    api.register_blueprint(TicketBlueprint)

    return app
```

### 6.3.  
Run the app
```
python run.py
http://localhost:5000/docs
```