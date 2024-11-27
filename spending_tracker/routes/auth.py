from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from spending_tracker.db import query_executor
from spending_tracker.helpers import parse_expense, check_password_hash, generate_password_hash
from spending_tracker.validators import email_validator, password_validator

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

    if not check_password_hash(hashed_password, password):
        return jsonify({"msg": "Invalid username or password."}), 401

    access_token = create_access_token(identity=user_id)
    return jsonify({"msg": f"Successfully logged in, {username}.", "access_token": access_token}), 200
# TODO - to be able to log in with email as well

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Registers a new user.
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

    db_password = generate_password_hash(user_password)
    query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
    query_executor(query, (username, user_email, db_password), get_result=False)
    return {}, 201



@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """
    Get the spending data for the logged-in user.
    """
    user_id = get_jwt_identity()

    query = "SELECT id, expense, value FROM expenses WHERE user_id = %s"
    spending_data = query_executor(query, (user_id,), get_result=True)

    return [parse_expense(expense) for expense in spending_data], 200