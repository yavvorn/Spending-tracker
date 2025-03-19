from flask import Blueprint, request
from spending_tracker.helpers import generate_password_hash, check_password_hash, parse_expense
from spending_tracker.models import User, db
from spending_tracker.validators import email_validator, password_validator
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError


users_bp = Blueprint('users', __name__)


@users_bp.route('/users', methods=['PATCH'])
@jwt_required()
def update_user():
    """
    Update an existing user. Supports partial updates.
    """
    user_id = get_jwt_identity()

    data = request.get_json()

    if not data:
        return {"error": "No update data provided."}, 400

    user_to_update = User.query.filter_by(id=user_id).first()

    if not user_to_update:
        return {"error": "User not found."}, 404

    updates_made = False

    if 'username' in data:
        new_username = data['username'].strip()
        if not new_username:
            return {"error": "Username cannot be empty."}, 400
        if new_username != user_to_update.username:
            user_to_update.username = new_username
            updates_made = True

    if 'email' in data:
        new_email = data['email'].strip()
        if not new_email:
            return {"error": "Email cannot be empty."}, 400
        if not email_validator(new_email):
            return {"error": "Invalid email address provided."}, 400
        if new_email != user_to_update.email:
            user_to_update.email = new_email
            updates_made = True

    if 'password' in data:
        new_password = data['password']
        if not new_password:
            return {"error": "Password cannot be empty."}, 400
        if not password_validator(new_password):
            return {
                "error": "Password must contain at least one uppercase letter, one number, and one special character."
            }, 400
        if not check_password_hash(user_to_update.password, new_password):
            user_to_update.password = generate_password_hash(new_password)
            updates_made = True

    if not updates_made:
        return {"error": "No changes detected in provided data."}, 400

    try:
        db.session.commit()
        return {}, 200

    except IntegrityError:
        db.session.rollback()
        return {"error": "Username or email already exists."}, 409

    except Exception as e:
        db.session.rollback()
        return {"error": "Failed to update user."}, 500


@users_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """
    Get the authenticated user's profile and their spending data.
    Returns user details and all associated expenses.
    """
    user_id = get_jwt_identity()

    user = User.query.filter_by(id=user_id).first()

    if not user:
        return {"error": "User not found."}, 404

    try:
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            #  "expenses": [parse_expense(expense) for expense in user.expenses] 
        }

        return user_data, 200

    except Exception as e:
        return {"error": "Failed to fetch user data."}, 500


@users_bp.route('/users', methods=['DELETE'])
@jwt_required()
def delete_user():
    """
    Deletes an existing user.
    """
    user_id = get_jwt_identity()

    try:
        user_to_delete = User.query.filter_by(id=user_id).first()
        if not user_to_delete:
            return {"error": "User not found."}, 404

        db.session.delete(user_to_delete)
        db.session.commit()

        return {}, 204

    except Exception as e:
        db.session.rollback()
        return {"error": "Failed to delete user."}, 500
