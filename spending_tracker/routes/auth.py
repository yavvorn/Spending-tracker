from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from spending_tracker.helpers import parse_expense, check_password_hash, generate_password_hash
from spending_tracker.models import User, db
from spending_tracker.validators import email_validator, password_validator

auth_bp = Blueprint("auth", __name__)

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

    new_user = User(
        username=username,
        email=user_email,
        password=db_password
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        return {}, 201

    except IntegrityError as e:
        db.session.rollback()
        return{"error": "Username or email already exists."}, 409 #  conflict

    except Exception as e:
        db.session.rollback()
        return {"error": "An error occurred with registration."}

@auth_bp.route("/login", methods=["POST"]) # TODO to support login via email?
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    if not username or not password:
        return jsonify({"msg": "Username and password are required."}), 400

    user_logging_in = User.query.filter_by(username=username).first()

    if not user_logging_in:
        return jsonify({"msg": "Invalid username or password."}), 401

    if not check_password_hash(user_logging_in.password, password):
        return jsonify({"msg": "Invalid username or password."}), 401

    access_token = create_access_token(identity=user_logging_in.id)
    return jsonify({"msg": f"Successfully logged in, {username}.", "access_token": access_token}), 200
    # Mock with postman, add tag Authorization and Value set with "Bearer {TOKEN}"

# TODO - to be able to log in with email as well
#
#
# # TODO this is supposed to return information about the user
# # @auth_bp.route("/me", methods=["GET"])
# # @jwt_required()
# # def me():
# #     """
# #     Get the spending data for the logged-in user.
# #     """
# #     user_id = get_jwt_identity()
# #
# #     query = "SELECT id, expense, value FROM expenses WHERE user_id = %s"
# #     spending_data = query_executor(query, (user_id,), get_result=True)
# #
# #     return [parse_expense(expense) for expense in spending_data], 200