from flask import Blueprint, request
from spending_tracker.db import query_executor
from spending_tracker.helpers import generate_password_hash, check_password_hash
from spending_tracker.models import User, db
from spending_tracker.validators import email_validator, password_validator
from flask_jwt_extended import get_jwt_identity, jwt_required

users_bp = Blueprint('users', __name__)


@users_bp.route('/users', methods=['PATCH'])  # TODO: Make this a PATCH request and support partial updates\
@jwt_required()
def update_user():
    """
    Update an existing user. Supports partial updates.
    """
    user_id = get_jwt_identity()

    data = request.get_json()

    new_username = data.get('username')
    new_user_email = data.get('email')
    new_user_password = data.get('password')

    user_to_update = User.query.filter_by(id=user_id).first()

    current_username = User.username
    current_email = User.email
    current_password = User.password

    if new_username != current_username:
        user_to_update.username = new_username

    if new_user_email != current_email:
        user_email = email_validator(new_user_email)
        if user_email == "Invalid Email.":
            return {"error": "Invalid email address provided."}, 400
        user_to_update.email = new_user_email

    if not password_validator(new_user_password):
        return {
            "error": "Password must contain at least one uppercase letter, "
                     "one number, and one special character."}, 400
    hashed_new_password = generate_password_hash(new_user_password)

    if hashed_new_password != current_password:
        user_to_update.password = hashed_new_password

    db.session.commit()

    return {}, 204


@users_bp.route('/users', methods=['DELETE'])
@jwt_required()
def delete_user():
    """
    Deletes an existing user.
    """
    user_id = get_jwt_identity()

    user_to_delete = User.query.filter_by(id=user_id).first()

    if not user_to_delete:
        return ({"error": "User not found."}), 404

    db.session.delete(user_to_delete)
    db.session.commit()

    return {}, 200
