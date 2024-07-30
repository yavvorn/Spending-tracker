from flask import Flask, request, g
from psycopg2 import pool
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

db_pool = pool.SimpleConnectionPool(
    1, 20,
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)


def get_db():
    if 'db' not in g:
        g.db = db_pool.getconn()
    return g.db


def create_cursor():
    conn = get_db()
    cur = conn.cursor()
    return cur, conn


def query_executor(query, args=None, get_result=True):
    """
    Connects to the database and executes an SQL query.
    :param cur: - instantiated cursor
    :param query: SQL query
    :param args: Placeholders for the SQL query
    :param get_result: whether or not a result ought to be returned
    :return: either a result or None
    """
    cur, conn = create_cursor()
    data = None

    try:
        if args is not None:
            cur.execute(query, args)
        else:
            cur.execute(query)
        conn.commit()
        if get_result:
            data = cur.fetchall()
        else:  # new
            data = {'message': 'Query executed successfully'}
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()  # new
    return data


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

    query = "INSERT INTO expenses (expense, value) VALUES (%s, %s)"
    expense = query_executor(query, (expense_name, expense_value), get_result=False)

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

    query = "UPDATE expenses SET expense = %s, value = %s WHERE id = %s"
    expense = query_executor(query, (expense_name, expense_value, expense_id), get_result=False)

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
