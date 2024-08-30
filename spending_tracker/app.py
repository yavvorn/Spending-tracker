import os

from flask import Flask, request, g
from dotenv import load_dotenv
from spending_tracker.db import query_executor
from spending_tracker.validators import validate_create_expense

load_dotenv()
app = Flask(__name__)


@app.route('/expenses', methods=["GET"])
def expense_data():
    """
    Returns all the expenses from the database.
    """
    data = query_executor("SELECT expense, value FROM expenses ORDER BY expense")
    if data is None:
        return {"error": "Cannot retrieve data"}
    return dict(data), 200


@app.route('/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    """
    Returns a particular expense and if nonexistent returns an error.
    """

    query = "SELECT expense, value FROM expenses WHERE id = %s"
    expense = query_executor(query, (expense_id,))

    if not expense:
        return {"error": "Expense doesn't exist"}, 404

    return dict(expense), 200


@app.route('/expenses', methods=['POST'])
def create_expense():
    """
    Creates a new expense
    """
    data = request.get_json()

    if not validate_create_expense(data):
        return {"error": "Invalid payload"}, 400

    expense_name = data.get('expense')
    expense_value = data.get('value')
    query = "INSERT INTO expenses (expense, value) VALUES (%s, %s)"
    query_executor(query, (expense_name, expense_value), get_result=False)
    return {}, 201


@app.route('/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id: int):
    """
    Update an already existing expense
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


@app.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """
    Removes an existing expense.
    """
    try:
        query = "DELETE FROM expenses WHERE id = %s"
        expense = query_executor(query, (expense_id,), get_result=False)
        return {}, 200

    except Exception as e:
        return {"error": "Expense not found."}, 404


if __name__ == '__main__':
    app.run(debug=os.getenv("ENVIRONMENT").lower() == "dev")
