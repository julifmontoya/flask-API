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
