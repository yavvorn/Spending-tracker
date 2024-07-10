from flask import Flask, request

app = Flask(__name__)

ALLOWED_CATEGORIES = ['Entertainment', 'Bills', 'Food', 'Cash', 'Necessities']
PATH_TO_CSV_FILE = '../spending.csv'

expenses = {
    1: {"id": 1, "expense": "Entertainment", "value": 50},
    2: {"id": 2, "expense": "Bills", "value": 50},
    3: {"id": 3, "expense": "Food", "value": 50},
    4: {"id": 4, "expense": "Necessities", "value": 50},
    5: {"id": 5, "expense": "Cash", "value": 10}
}


# TODO - ERROR HANDLING

@app.route('/expenses', methods=['GET'])
def expense_data():
    """
    Returns all of the expenses.
    """
    return expenses.values()


@app.route('/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    """
    Returns a particular expense and if nonexistent returns an error.
    """
    expense = expenses.get(expense_id)
    if expense is None:
        return {'error': 'Transaction not found'}, 404
    return expense


@app.route('/expenses', methods=['POST'])
def create_expense():
    """
    Creates a new expense.
    """
    new_id = len(expenses) + 1
    new_expense = {'id': new_id, 'expense': request.json['expense'], 'value': request.json['value']}
    expenses[new_id] = new_expense
    return new_expense, 201


@app.route('/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """
    Updates an already existing expense.
    """
    expense = expenses.get(expense_id)
    if expense is None:
        return {'error': 'Transaction not found'}, 404

    expense['expense'] = request.json['expense']
    expense['value'] = request.json['value']
    return expense


@app.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """
    Removes an existing expense.
    """

    try:
        del expenses[expense_id]
    except KeyError:
        return {"error": "Transaction doesn't exist"}, 404

    return {"message": f"Expense {expense_id} removed successfully"}


@app.route('/statistics', methods=['GET'])
def get_statistics():
    """
    Gets and displays the statistics.
    """
    overall_usage = {}
    for expense in expenses.values():
        if expense['expense'] not in overall_usage.keys():
            overall_usage[expense['expense']] = expense['value']
        else:
            overall_usage[expense['expense']] += expense['value']

    return overall_usage


if __name__ == '__main__':
    app.run(debug=True)
