from flask import Blueprint, request
from spending_tracker.db import query_executor
from spending_tracker.helpers import parse_expense
from spending_tracker.validators import validate_create_expense
from flask_jwt_extended import get_jwt_identity, jwt_required
from spending_tracker.models import Expenses, db


expenses_bp = Blueprint('expenses', __name__)


@expenses_bp.route('/expenses', methods=["GET"])
@jwt_required()
def expense_data():
    """
    Get the spending data for the logged-in user.
    """
    user_id = get_jwt_identity()

    expenses_to_get = Expenses.query.filter_by(user_id=user_id).all()
    return [parse_expense(expense) for expense in expenses_to_get], 200



@expenses_bp.route('/expenses/<int:expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    """
    Returns a particular expense or an error if it doesn't exist.
    """
    user_id = get_jwt_identity()
    expense_to_get = Expenses.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense_to_get:
        return {"error": "Expense doesn't exist"}, 404
    return parse_expense(expense_to_get), 200


@expenses_bp.route('/expenses', methods=['POST'])
@jwt_required()
def create_expense():
    """
    Creates a new expense.
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    expense_name = data.get('expense')
    expense_value = data.get('value')

    new_expense = Expenses(
        expense_name=expense_name,
        expense_value=expense_value,
        user_id=user_id
    )

    if not validate_create_expense(data):
        return {"error": "Invalid payload"}, 400

    try:
        db.session.add(new_expense)
        db.session.commit()
        return {}, 201
    except Exception as e:
        db.session.rollback()
        return {"error": f"Error occurred - {e!r}"}, 409


@expenses_bp.route('/expenses/<int:expense_id>', methods=['PATCH'])
@jwt_required()
def update_expense(expense_id: int):
    """
    Updates an existing expense.
    """
    data = request.get_json()
    user_id = get_jwt_identity()

    expense_to_update = Expenses.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense_to_update:
        return {"error": "Expense not found"}, 404

    updates_made = False

    if not validate_create_expense(data):
        return {"error": "Invalid payload"}, 400

    new_expense_name = data.get('expense')
    new_expense_value = data.get('value')

    if "expense" in data:
        if expense_to_update.expense_name != new_expense_name:
            expense_to_update.expense_name = new_expense_name
            updates_made = True

    if "value" in data:
        if expense_to_update.expense_value != new_expense_value:
            expense_to_update.expense_value = new_expense_value
            updates_made = True

    if updates_made:
        try:
            db.session.commit()
            return {}, 204
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error occurred - {e!r}"}, 500


@expenses_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    """
    Deletes an existing expense.
    """
    user_id = get_jwt_identity()

    expense_to_delete = Expenses.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense_to_delete:
        return ({"error": "Expense not found."}), 404

    db.session.delete(expense_to_delete)
    db.session.commit()

    return {}, 200

