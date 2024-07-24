from flask import Flask, request, jsonify, g, render_template, redirect, url_for
from config import db_pool

app = Flask(__name__)


# Function to get connection from the pool - it checks if a database
# is connected to the Flask obj g and if there isn't it connects the db to it
def get_db():
    if 'db' not in g:
        g.db = db_pool.getconn()
    return g.db


def create_cursor():
    conn = get_db()
    cur = None
    try:
        cur = conn.cursor()
    except Exception as e:
        return None  # should it return something else in this case?
    return cur, conn


def query_executor_get(cur, query, args=None):
    data = None
    try:
        if args is not None:
            cur.execute(query, args)
        else:
            cur.execute(query)
        data = cur.fetchall()
    except TypeError as e:
        return {"error": str(e)}, 400
    finally:
        if cur is not None:
            cur.close()
    return data


def query_executor_post(cur, query, args=None):
    try:
        if args is not None:
            cur.execute(query, args)
        else:
            cur.execute(query)
    except TypeError as e:
        return {"error": str(e)}, 400  # Returning a dictionary with an error message and HTTP status code
    finally:
        if cur is not None:
            cur.close()
    return "Action carried out successfully!"  # this is also applied to PUT and  POST


# Function to close connection and return it to the pool - once a request is done,
# the connection is returned to the pool in order to be re-used - this is done automatically by Flask
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
    cur, conn = create_cursor()
    data = query_executor_get(cur, "SELECT expense, value FROM expenses ORDER BY expense")
    if data is None:
        return {"error": "Cannot retrieve data"}

    return dict(data), 200


@app.route('/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    """
    Returns a particular expense and if nonexistent returns an error.
    """
    cur, conn = create_cursor()
    query = "SELECT expense, value FROM expenses WHERE id = %s"
    expense = query_executor_get(cur, query, (expense_id,))

    if not expense:
        return {"error": "Expense doesn't exist"}, 404

    return dict(expense), 200


@app.route('/expenses', methods=['POST'])
def create_expense():
    """
    Creates a new expense
    """
    data = request.get_json()
    # what exactly happens here when the request doesn't come from the front end?
    # How is the data extracted from the postman/terminal? Is this the only way this can work?
    expense_name = data.get('expense')
    expense_value = data.get('value')

    # this is how it used to be, is this how it should be once we have frontend?
    # expense_name = request.json['expense']
    # expense_value = request.json['value']
    cur, conn = create_cursor()
    query = "INSERT INTO expenses (expense, value) VALUES (%s, %s)"
    expense = query_executor_post(cur, query, (expense_name, expense_value))
    conn.commit()

    return expense, 201


@app.route('/update', methods=['PUT'])
def update_expense():
    """
    Update an already existing expense
    """
    data = request.get_json()

    expense_name = data.get('expense')
    expense_value = data.get('value')
    expense_id = data.get("id")

    cur, conn = create_cursor()
    query = "UPDATE expenses SET expense = %s, value = %s WHERE id = %s"
    expense = query_executor_post(cur, query, (expense_name, expense_value, expense_id))
    conn.commit()

    return expense, 204  # it's not printing the string from the query_executor_post


@app.route('/delete/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """
    Removes an existing expense.
    """

    cur, conn = create_cursor()
    query = "DELETE FROM expenses WHERE id = %s"
    expense = query_executor_post(cur, query, (expense_id,))
    conn.commit()

    if not expense:
        return {"error": "Cannot retrieve expense"}, 404

    return expense


if __name__ == '__main__':
    app.run(debug=True)
