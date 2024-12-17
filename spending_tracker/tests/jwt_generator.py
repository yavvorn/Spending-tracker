from spending_tracker.app import app
import jwt
from datetime import datetime, timedelta


def generate_mock_jwt():
    payload = {
        "sub": 1,
        "exp": datetime.utcnow() + timedelta(seconds=app.config["JWT_ACCESS_TOKEN_EXPIRES"]),
    }
    secret_key = app.config["JWT_SECRET_KEY"]
    algorithm = "HS256"
    return jwt.encode(payload, secret_key, algorithm=algorithm)