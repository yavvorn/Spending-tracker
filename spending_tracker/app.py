from flask import Flask, request, g
from dotenv import load_dotenv
from spending_tracker.db import db_pool, query_executor

load_dotenv()
app = Flask(__name__)


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db_pool.putconn(db)


@app.route('/', methods=["GET"])
def expense_data():
    """
    Returns all the expenses from the database.
    """
    data = query_executor("SELECT expense, value FROM expenses ORDER BY expense")
    if data is None:
        return {"error": "Cannot retrieve data"}
    return dict(data), 200


@app.route('/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    """
    Returns a particular expense and if nonexistent returns an error.
    """

    query = "SELECT expense, value FROM expenses WHERE id = %s"
    expense = query_executor(query, (expense_id,))

    if not expense:
        return {"error": "Expense doesn't exist"}, 404

    return dict(expense), 200


@app.route('/expenses', methods=['POST'])
def create_expense():
    """
    Creates a new expense
    """
    data = request.get_json()

    expense_name = data.get('expense')
    expense_value = data.get('value')

    try:
        query = "INSERT INTO expenses (expense, value) VALUES (%s, %s)"
        query_executor(query, (expense_name, expense_value), get_result=False)
        return {}, 201
    except Exception as e:
        return {"error": "Failed to create expense"}, 500


@app.route('/update', methods=['PUT'])
def update_expense():
    """
    Update an already existing expense
    """
    data = request.get_json()

    expense_name = data.get('expense')
    expense_value = data.get('value')

    expense_id = data.get("id")

    query = "UPDATE expenses SET expense = %s, value = %s WHERE id = %s"
    expense = query_executor(query, (expense_name, expense_value, expense_id), get_result=False)

    if not expense:
        return {"error": "Expense doesn't exist"}, 404

    return expense, 204


@app.route('/delete/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """
    Removes an existing expense.
    """
    query = "DELETE FROM expenses WHERE id = %s"
    expense = query_executor(query, (expense_id,), get_result=False)

    if not expense:
        return {"error": "Cannot retrieve expense"}, 404

    return expense


if __name__ == '__main__':
    app.run(debug=True)
