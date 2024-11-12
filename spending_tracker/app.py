import os
from flask import Flask
from dotenv import load_dotenv
from spending_tracker.extensions import bcrypt
from spending_tracker.routes.users import users_bp
from spending_tracker.routes.expenses import expenses_bp

from flask_jwt_extended import JWTManager
from spending_tracker.routes.auth import auth_bp

load_dotenv()
app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # expires in 1h

jwt = JWTManager(app)
bcrypt.init_app(app)


app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(users_bp)
app.register_blueprint(expenses_bp)

if __name__ == '__main__':
    app.run(debug=os.getenv("ENVIRONMENT").lower() == "dev")
