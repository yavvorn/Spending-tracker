import os
from flask import Flask
from dotenv import load_dotenv
from spending_tracker.helpers import bcrypt
from spending_tracker.routes.users import users_bp
from spending_tracker.routes.expenses import expenses_bp
from flask_jwt_extended import JWTManager
from spending_tracker.routes.auth import auth_bp
from spending_tracker.models import db


load_dotenv()
app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # expires in 1h

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")  # Replace with your DB URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Suppress unnecessary warnings

db.init_app(app)
jwt = JWTManager(app)
bcrypt.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(expenses_bp)

if __name__ == '__main__':
    app.run(debug=os.getenv("ENVIRONMENT").lower() == "dev")
