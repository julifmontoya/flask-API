from app.extensions import ma
from app.models.ticket import Ticket

class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        load_instance = True
        ref = "Ticket"  # ✅ Tells Swagger to always use the name "Ticket"
