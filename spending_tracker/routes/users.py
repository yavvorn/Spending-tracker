from flask import Blueprint, request
from spending_tracker.extensions import bcrypt
from spending_tracker.db import query_executor
from spending_tracker.helpers import password_hash
from spending_tracker.validators import email_validator, password_validator

users_bp = Blueprint('users', __name__)


@users_bp.route('/users', methods=['POST'])
def create_user():
    """
    Creates a new user.
    """
    data = request.get_json()
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


@users_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id: int):
    """
    Update an existing user.
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


@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Deletes an existing user.
    """
    try:
        query = "DELETE FROM users WHERE id = %s"
        query_executor(query, (user_id,), get_result=False)
        return {}, 200
    except Exception as e:
        return {"error": "User not found."}, 404
