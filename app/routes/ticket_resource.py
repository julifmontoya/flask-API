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
