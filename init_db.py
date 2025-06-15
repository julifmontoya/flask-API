from app import create_app
from app.extensions import db
from app.models.ticket import Ticket  # Import all models to register them

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Database initialized.")