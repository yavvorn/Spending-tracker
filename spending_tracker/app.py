from flask import Flask, request, jsonify, g, render_template, redirect, url_for
import psycopg2
from psycopg2 import pool

app = Flask(__name__)

ALLOWED_CATEGORIES = ['Entertainment', 'Bills', 'Food', 'Cash', 'Necessities']
PATH_TO_CSV_FILE = '../spending.csv'

db_pool = pool.SimpleConnectionPool(1, 20, database="Finance_tracker",
                                    user="postgres",
                                    password="pass1234!",
                                    host="localhost", port="5432")

# Function to get connection from the pool
def get_db():
    if 'db' not in g:
        g.db = db_pool.getconn()
    return g.db

# Function to close connection and return it to the pool
@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db_pool.putconn(db)


@app.route('/')
def index():
    conn = get_db()
    cur = None
    data = []
    try:
        # Create a cursor
        cur = conn.cursor()

        # Select all expenses from the table
        cur.execute("SELECT * FROM expenses ORDER BY expense")

        # Fetch the data
        data = cur.fetchall()
    finally:
        if cur is not None:
            cur.close()

    return render_template('index.html', data=data)

# @app.route('/expenses/<int:expense_id>', methods=['GET'])
# def get_expense(expense_id):
#     """
#     Returns a particular expense and if nonexistent returns an error.
#     """
#     expense = expenses.get(expense_id)
#     if expense is None:
#         return {'error': 'Transaction not found'}, 404
#     return expense


@app.route('/create', methods=['POST'])
def create_expense():
    # Handle form data
    conn = get_db()
    cur = None

    try:
        # Parse form data from request
        expense_name = request.form['expense'] # expects standard application/x-www-form-urlencoded content-type
        expense_value = request.form['value']

        # Create a cursor object using the connection
        cur = conn.cursor()

        # Execute a query to insert new expense into the table
        cur.execute("INSERT INTO expenses (expense, value) VALUES (%s, %s)", (expense_name, expense_value))
        conn.commit()  # Commit the transaction

        return redirect(url_for('index'))

        # Return new expense as JSON with HTTP status code 201 (Created)
    except Exception as e:
        conn.rollback()  # Rollback the transaction in case of error
        return str(e), 400  # Return error message with HTTP status code 400 (Bad Request)
    finally:
        if cur is not None:
            cur.close()


@app.route('/update', methods=['POST'])
def update_expense():
    conn = get_db()
    cur = None

    try:
        # Parse form data from request
        expense_id = request.form['expense_id']
        expense_name = request.form['expense']
        expense_value = request.form['value']

        # Create a cursor object using the connection
        cur = conn.cursor()

        # Execute a query to update the expense in the table
        cur.execute("UPDATE expenses SET expense = %s, value = %s WHERE id = %s", (expense_name, expense_value, expense_id))
        conn.commit()  # Commit the transaction

        return redirect(url_for('index'))

    except Exception as e:
        conn.rollback()  # Rollback the transaction in case of error
        return str(e), 400  # Return error message with HTTP status code 400 (Bad Request)
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()  # Close the connection



@app.route('/delete/<int:expense_id>', methods=['DELETE', 'POST'])
def delete_expense(expense_id):
    """
    Removes an existing expense.
    """
    conn = get_db()
    cur = None
    try:
        # Create a cursor object using the connection
        cur = conn.cursor()

        # Execute a query to delete expense from the table
        cur.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        conn.commit()  # Commit the transaction

        return redirect(url_for('index'))

    except Exception as e:
        conn.rollback()  # Rollback the transaction in case of error
        return str(e), 400  # Return error message with HTTP status code 400 (Bad Request)

    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


# @app.route('/statistics', methods=['GET'])
# def get_statistics():
#     """
#     Gets and displays the statistics.
#     """
#     overall_usage = {}
#     for expense in expenses.values():
#         if expense['expense'] not in overall_usage.keys():
#             overall_usage[expense['expense']] = expense['value']
#         else:
#             overall_usage[expense['expense']] += expense['value']
#
#     return overall_usage


if __name__ == '__main__':
    app.run(debug=True)
