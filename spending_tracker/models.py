from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(db.Model):
    """
    DB which includes:
    id - primary key
    username - username used by user, must be unique
    password - hashed password of user
    created_at - when account created 
    spending_data = collection of spending made by user 
    """

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.VARCHAR(64), unique=True, nullable=False)
    password = db.Column(db.VARCHAR(64), unique=False, nullable=False)
    email = db.Column(db.VARCHAR(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    expenses = db.relationship('Expenses', backref='user', lazy=True,
                               cascade='all, delete-orphan')

class Expenses(db.Model):
    """
    DB which includes:
    id - primary key
    value -  value of the expense
    date_time_of_transaction - when the transaction occurred
    user_id - foreign key linking to the user who made the transaction
    """
    __tablename__ = "expenses"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    expense_name = db.Column(db.String(50), nullable=False)
    expense_value = db.Column(db.NUMERIC(12, 2), primary_key=True)
    date_time_of_expense = db.Column(db.DateTime, nullable=False, server_default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)