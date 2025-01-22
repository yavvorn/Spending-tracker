from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    """
    DB which includes:
    id - primary key
    username - username used by user, must be unique
    password - hashed password of user
    created_at - when account created 
    spending_data = collection of spending made by user 
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    # spending_data = db.relationship('SpendingData', backref='user', lazy=True)

