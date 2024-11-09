import os
from flask_bcrypt import Bcrypt
from flask import Flask, request, g
from dotenv import load_dotenv
from spending_tracker.db import query_executor
from spending_tracker.helpers import parse_expense, password_hash
from spending_tracker.validators import validate_create_expense, email_validator, password_validator

load_dotenv()
app = Flask(__name__)


@app.route('/expenses', methods=["GET"])
def expense_data():
    """
    Returns all the expenses from the database.
    """
    data = query_executor("SELECT id, expense, value FROM expenses ORDER BY id")
    if data is None:
        return {"error": "Cannot retrieve data"}
    return [parse_expense(expense) for expense in data], 200


@app.route('/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    """
    Returns a particular expense and if nonexistent returns an error.
    """

    query = "SELECT id, expense, value FROM expenses WHERE id = %s"
    query_result = query_executor(query, (expense_id,))

    if not query_result:
        return {"error": "Expense doesn't exist"}, 404

    return parse_expense(query_result[0]), 200


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
    user_id = data.get('user_id')  # TODO - tva trqq se vzima ot sesiqta, nz kak - use JWT TOKENS AUTH
    query = "INSERT INTO expenses (expense, value, user_id) VALUES (%s, %s, %s)"
    query_executor(query, (expense_name, expense_value, user_id), get_result=False)
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


# TODO papka routers - expense/users


@app.route('/users', methods=['POST'])
def create_user():
    """
    Creates a new user.
    """

    data = request.get_json()
    bcrypt = Bcrypt(app)

    username = data.get('username')
    user_email = data.get('email')
    user_password = data.get('password')

    validated_email = email_validator(user_email)
    if validated_email == "Invalid Email.":
        return {"error": "Invalid email address provided."}, 400

    if not password_validator(user_password):
        return {
            "error": "Password must contain at least one uppercase letter, one number, and one special character."}, 400

    db_password = password_hash(user_password, bcrypt)

    query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
    query_executor(query, (username, user_email, db_password), get_result=False)
    return {}, 201


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id: int):
    """
    Update an already existing user
    """
    data = request.get_json()

    username = data.get('username')
    user_email = data.get('email')
    user_password = data.get('password')

    query = "UPDATE users SET username = %s, email = %s, password = %s WHERE id = %s"
    try:
        query_executor(query, (username, user_email, user_password, user_id), get_result=False)
    except Exception as e:
        print(f"{e!r}")

    return {}, 204


# TODO /me - who is you

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Deletes an existing user.
    """

    try:
        query = "DELETE FROM users WHERE id = %s"
        user = query_executor(query, (user_id,), get_result=False)
        return {}, 200

    except Exception as e:  # even if deletion unsuccessful, it doesn't get to here
        return {"error": "User not found."}, 404


if __name__ == '__main__':
    app.run(debug=os.getenv("ENVIRONMENT").lower() == "dev")
