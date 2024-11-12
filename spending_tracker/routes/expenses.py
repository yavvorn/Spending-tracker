from flask import Blueprint, request
from spending_tracker.db import query_executor
from spending_tracker.helpers import parse_expense
from spending_tracker.validators import validate_create_expense

expenses_bp = Blueprint('expenses', __name__)


@expenses_bp.route('/expenses', methods=["GET"])
def expense_data():
    """
    Returns all the expenses from the database.
    """
    data = query_executor("SELECT id, expense, value FROM expenses ORDER BY id")
    if data is None:
        return {"error": "Cannot retrieve data"}
    return [parse_expense(expense) for expense in data], 200


@expenses_bp.route('/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    """
    Returns a particular expense or an error if it doesn't exist.
    """
    query = "SELECT id, expense, value FROM expenses WHERE id = %s"
    query_result = query_executor(query, (expense_id,))

    if not query_result:
        return {"error": "Expense doesn't exist"}, 404

    return parse_expense(query_result[0]), 200


@expenses_bp.route('/expenses', methods=['POST'])
def create_expense():
    """
    Creates a new expense.
    """
    data = request.get_json()

    if not validate_create_expense(data):
        return {"error": "Invalid payload"}, 400

    expense_name = data.get('expense')
    expense_value = data.get('value')
    user_id = data.get('user_id')  # Placeholder for user session authentication
    query = "INSERT INTO expenses (expense, value, user_id) VALUES (%s, %s, %s)"
    query_executor(query, (expense_name, expense_value, user_id), get_result=False)
    return {}, 201


@expenses_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id: int):
    """
    Updates an existing expense.
    """
    data = request.get_json()

    if not validate_create_expense(data):
        return {"error": "Invalid payload"}, 400

    expense_name = data.get('expense')
    expense_value = data.get('value')

    query = "UPDATE expenses SET expense = %s, value = %s WHERE id = %s"
    try:
        query_executor(query, (expense_name, expense_value, expense_id), get_result=False)
    except Exception as e:
        print(f"{e!r}")

    return {}, 204


@expenses_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """
    Deletes an existing expense.
    """
    try:
        query = "DELETE FROM expenses WHERE id = %s"
        query_executor(query, (expense_id,), get_result=False)
        return {}, 200
    except Exception as e:
        return {"error": "Expense not found."}, 404
