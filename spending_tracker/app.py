import os
from flask import Flask
from dotenv import load_dotenv
from spending_tracker.extensions import bcrypt
from routes.users import users_bp
from routes.expenses import expenses_bp

load_dotenv()
app = Flask(__name__)
bcrypt.init_app(app)

app.register_blueprint(users_bp)
app.register_blueprint(expenses_bp)

if __name__ == '__main__':
    app.run(debug=os.getenv("ENVIRONMENT").lower() == "dev")
