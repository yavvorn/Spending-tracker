from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    if username == "testuser" and password == "testpassword": # test user val
        user_id = 12345  # assign example user_id here but should come from the db
        access_token = create_access_token(identity=user_id)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401


@auth_bp.route("/protected", methods=["GET"])  # to confirm the token auth is working
@jwt_required()  # this decorator says only requests with a valid token can access this route
# the decorator is needed for any user-specific route
def protected():
    current_user = get_jwt_identity()  # extracts the user's identity from the token (in this case the user_id)
    # also needed for any user-specific route
    return jsonify(logged_in_as=current_user), 200