from datetime import datetime, time, timedelta
from flask_bcrypt import Bcrypt
from flask_jwt_extended import get_jwt_identity
from spending_tracker.models import Expenses
from sqlalchemy import func

bcrypt = Bcrypt()


def parse_expense(expense):
    return {
        "id": getattr(expense, "id", None),
        "expense": getattr(expense, "expense_name", None),
        "value": float(getattr(expense, "expense_value", 0))
    }


def generate_password_hash(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')


def check_password_hash(hashed_password, password):
    return bcrypt.check_password_hash(hashed_password, password)


def get_daily_expenses():
    """
    Get expenses for the current day.
    """
    user_id = get_jwt_identity()
    today = datetime.now().date()

    return Expenses.query.filter_by(user_id=user_id) \
        .filter(func.date(Expenses.date_time_of_expense) == today) \
        .all()


def get_weekly_expenses():
    """
    Get expenses for the last 7 days.
    """
    user_id = get_jwt_identity()
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    start_of_week = datetime.combine(week_ago, time.min)
    end_of_day = datetime.combine(today, time.max)

    return Expenses.query.filter_by(user_id=user_id) \
        .filter(Expenses.date_time_of_expense >= start_of_week) \
        .filter(Expenses.date_time_of_expense <= end_of_day) \
        .all()


def get_monthly_expenses():
    """
    Get expenses for the last 30 days.
    """
    user_id = get_jwt_identity()
    today = datetime.now().date()
    month_ago = today - timedelta(days=30)
    start_of_month = datetime.combine(month_ago, time.min)
    end_of_day = datetime.combine(today, time.max)

    return Expenses.query.filter_by(user_id=user_id) \
        .filter(Expenses.date_time_of_expense >= start_of_month) \
        .filter(Expenses.date_time_of_expense <= end_of_day) \
        .all()
