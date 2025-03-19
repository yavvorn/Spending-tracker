from flask import Blueprint, request
from spending_tracker.helpers import parse_expense, get_daily_expenses, get_weekly_expenses, get_monthly_expenses
from spending_tracker.validators import validate_create_expense
from flask_jwt_extended import get_jwt_identity, jwt_required
from spending_tracker.models import Expenses, db


expenses_bp = Blueprint('expenses', __name__)


@expenses_bp.route('/expenses', methods=["GET"])
@jwt_required()
def expense_data():
    """
    Get the spending data for the logged-in user.
    """
    user_id = get_jwt_identity()

    try:
        expenses_to_get = (Expenses.query.filter_by(user_id=user_id).
                           order_by(Expenses.date_time_of_expense.desc()).all())

        if not expenses_to_get:
            return { "error": "No expenses found."}, 200

        return {"expenses": [parse_expense(expense) for expense in expenses_to_get]}, 200

    except Exception as e:
        return {"error": "Failed to retrieve expenses."}, 500


@expenses_bp.route('/expenses/day', methods=['GET'])
@jwt_required()
def daily_expenses():
    try:
        expenses = get_daily_expenses()

        if not expenses:
            return {"error": "No expenses found for today."}, 200

        return {
            "message": "Daily expenses retrieved successfully.",
            "expenses": [parse_expense(expense) for expense in expenses],
            "total": float(sum(expense.expense_value for expense in expenses))}, 200

    except Exception as e:
        return {"error": "Failed to retrieve daily expenses."}, 500


@expenses_bp.route('/expenses/week', methods=['GET'])
@jwt_required()
def weekly_expenses():
    """
    Get expenses for the logged-in user for the last 7 days.
    Returns a list of expenses sorted by date (newest first).
    """
    try:
        expenses = get_weekly_expenses()

        if not expenses:
            return {"error": "No expenses found for the past week."}, 200

        return {
            "message": "Weekly expenses retrieved successfully.",
            "expenses": [parse_expense(expense) for expense in expenses],
            "total": float(sum(expense.expense_value for expense in expenses))}, 200

    except Exception as e:
        return {"error": "Failed to retrieve weekly expenses."}, 500

@expenses_bp.route('/expenses/month', methods=['GET'])
@jwt_required()
def monthly_expenses():
    """
    Get expenses for the logged-in user for the last 30 days.
    Returns a list of expenses sorted by date (newest first).
    """
    try:
        expenses = get_monthly_expenses()

        if not expenses:
            return {
                "error": "No expenses found for the past month."}, 200

        return {
            "message": "Monthly expenses retrieved successfully.",
            "expenses": [parse_expense(expense) for expense in expenses],
            "total": float(sum(expense.expense_value for expense in expenses))}, 200

    except Exception as e:
        return {"error": "Failed to retrieve monthly expenses."}, 500


@expenses_bp.route('/expenses/<int:expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    """
    Get a specific expense by ID for the logged-in user.
    Returns the expense details or an error if it doesn't exist.
    """
    user_id = get_jwt_identity()

    try:
        expense_to_get = Expenses.query.filter_by(id=expense_id, user_id=user_id).first()

        if not expense_to_get:
            return {"error": "Expense not found."}, 404

        return {"expense": parse_expense(expense_to_get)}, 200

    except Exception as e:
        return {"error": "Failed to retrieve expense."}, 500


@expenses_bp.route('/expenses', methods=['POST'])
@jwt_required()
def create_expense():
    """
    Creates a new expense.
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not validate_create_expense(data):
        return {"error": "Invalid payload."}, 400

    try:
        expense_name = data.get('expense')
        expense_value = data.get('value')

        new_expense = Expenses(
            expense_name=expense_name,
            expense_value=expense_value,
            user_id=user_id
        )

        db.session.add(new_expense)
        db.session.commit()

        return {
            "message": "Expense created successfully.",
            "expense": parse_expense(new_expense)
        }, 201

    except Exception as e:
        db.session.rollback()
        return {"error": f"Error occurred - {e!r}"}, 409


@expenses_bp.route('/expenses/<int:expense_id>', methods=['PATCH'])
@jwt_required()
def update_expense(expense_id: int):
    """
    Updates an existing expense.
    """
    data = request.get_json()
    user_id = get_jwt_identity()
    updates_made = False

    if not validate_create_expense(data):
        return {"error": "Invalid payload."}, 400

    expense_to_update = Expenses.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense_to_update:
        return {"error": "Expense not found."}, 404

    if "expense" in data:
        new_expense_name = data.get('expense')
        if expense_to_update.expense_name != new_expense_name:
            expense_to_update.expense_name = new_expense_name
            updates_made = True

    if "value" in data:
        new_expense_value = data.get('value')
        if expense_to_update.expense_value != new_expense_value:
            expense_to_update.expense_value = new_expense_value
            updates_made = True

    if updates_made:
        try:
            db.session.commit()
            return {"updated expense": parse_expense(expense_to_update)}, 200

        except Exception as e:
            db.session.rollback()
            return {"error": f"Error occurred - {e!r}"}, 500


@expenses_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    """
    Deletes an existing expense.
    """
    user_id = get_jwt_identity()

    expense_to_delete = Expenses.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense_to_delete:
        return {"error": "Expense not found."}, 404

    try:
        db.session.delete(expense_to_delete)
        db.session.commit()
        return {"message": "Expense deleted successfully."}, 200

    except Exception as e:
        db.session.rollback()
        return {"error": "Failed to delete expense."}, 500

#maybe func to return expenses for a specific date/date range