from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from spending_tracker.db import query_executor
from spending_tracker.extensions import bcrypt
from spending_tracker.helpers import parse_expense

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    if not username or not password:
        return jsonify({"msg": "Username and password are required."}), 400

    query = "SELECT id, password FROM users WHERE username = %s"
    user_data = query_executor(query, (username,), get_result=True)

    if not user_data:
        return jsonify({"msg": "Invalid username or password."}), 401

    user_id, hashed_password = user_data[0]

    if not bcrypt.check_password_hash(hashed_password, password):
        return jsonify({"msg": "Invalid username or password."}), 401

    access_token = create_access_token(identity=user_id)
    return jsonify({"msg": f"Successfully logged in, {username}.", "access_token": access_token}), 200
# TODO - to be able to log in with email as well


@auth_bp.route("/protected", methods=["GET"])  # to confirm the token auth is working
@jwt_required()  # this decorator says only requests with a valid token can access this route
# the decorator is needed for any user-specific route
def protected():
    current_user = get_jwt_identity()  # extracts the user's identity from the token (in this case the user_id)
    # also needed for any user-specific route
    return jsonify(logged_in_as=current_user), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_spendings():
    """
    Get the spending data for the logged-in user.
    """
    user_id = get_jwt_identity()

    query = "SELECT id, expense, value FROM expenses WHERE user_id = %s"
    spending_data = query_executor(query, (user_id,), get_result=True)

    return [parse_expense(expense) for expense in spending_data], 200