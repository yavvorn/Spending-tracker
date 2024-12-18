from flask import Blueprint, request
from spending_tracker.db import query_executor
from spending_tracker.helpers import parse_expense
from spending_tracker.validators import validate_create_expense
from flask_jwt_extended import get_jwt_identity, jwt_required


expenses_bp = Blueprint('expenses', __name__)


@expenses_bp.route('/expenses', methods=["GET"])
@jwt_required()
def expense_data():
    """
    Get the spending data for the logged-in user.
    """
    user_id = get_jwt_identity()

    query = "SELECT id, expense, value FROM expenses WHERE user_id = %s"
    spending_data = query_executor(query, (user_id,), get_result=True)

    return [parse_expense(expense) for expense in spending_data], 200


@expenses_bp.route('/expenses/<int:expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    """
    Returns a particular expense or an error if it doesn't exist.
    """
    user_id = get_jwt_identity()
    query = f"SELECT id, expense, value FROM expenses WHERE id = %s AND user_id = %s"
    query_result = query_executor(query, (expense_id, user_id))

    if not query_result:
        return {"error": "Expense doesn't exist"}, 404

    return parse_expense(query_result[0]), 200


@expenses_bp.route('/expenses', methods=['POST'])
@jwt_required()
def create_expense():
    """
    Creates a new expense.
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not validate_create_expense(data):
        return {"error": "Invalid payload"}, 400

    expense_name = data.get('expense')
    expense_value = data.get('value')
    query = "INSERT INTO expenses (expense, value, user_id) VALUES (%s, %s, %s)"
    query_executor(query, (expense_name, expense_value, user_id), get_result=False)
    return {}, 201


@expenses_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id: int):
    """
    Updates an existing expense.
    """
    data = request.get_json()
    user_id = get_jwt_identity()

    if not validate_create_expense(data):
        return {"error": "Invalid payload"}, 400

    expense_name = data.get('expense')
    expense_value = data.get('value')

    query = "UPDATE expenses SET expense = %s, value = %s WHERE id = %s AND user_id = %s"
    try:
        query_executor(query, (expense_name, expense_value, expense_id, user_id), get_result=False)
    except Exception as e:
        print(f"{e!r}")

    return {}, 204


@expenses_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    """
    Deletes an existing expense.
    """
    user_id = get_jwt_identity()
    try:
        query = "DELETE FROM expenses WHERE id = %s AND user_id = %s"
        query_executor(query, (expense_id, user_id), get_result=False)
        return {}, 200
    except Exception as e:
        return {"error": "Expense not found."}, 404
