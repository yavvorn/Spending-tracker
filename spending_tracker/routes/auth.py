import time
from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from spending_tracker.helpers import check_password_hash, generate_password_hash
from spending_tracker.models import User, db
from spending_tracker.validators import email_validator, password_validator


auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Registers a new user.
    """
    data = request.get_json()
    if not data:
        return {"error": "Missing request data"}, 400

    username = data.get('username')
    user_email = data.get('email')
    user_password = data.get('password')

    if not username or not user_email or not user_password: #  check if not empty
        return {"error": "Username, email, and password are required"}, 400

    if len(username) < 3: #  check if not short
        return {"error": "Username must be at least 3 characters"}, 400

    if not email_validator(user_email):
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
        return {"error": "Username or email already exists."}, 409 #  conflict

    except Exception as e:
        db.session.rollback()
        return {"error": "An error occurred with registration."}

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticates a user and returns an access token.
    """
    data = request.get_json()
    if not data:
        return {"error": "Missing request data"}, 400

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    identifier = email if not username and email else username #  email, ako nema username inak username

    if not identifier or not password:
        return {"error": "Username/email and password are required"}, 400

    if '@' in identifier:
        user_logging_in = User.query.filter_by(email=identifier).first()
    else:
        user_logging_in = User.query.filter_by(username=identifier).first()

    if not user_logging_in:
        return {"error": "Invalid credentials"}, 401

    if not check_password_hash(user_logging_in.password, password):
        time.sleep(0.5)  #  Prevent timing attacks
        return {"error": "Invalid credentials"}, 401

    access_token = create_access_token(identity=user_logging_in.id)

    return {"msg": f"Successfully logged in, {username}.", "access_token": access_token}, 200
    # if you log with email, username is empty
    # Mock with postman, add tag Authorization and Value set with "Bearer {TOKEN}"