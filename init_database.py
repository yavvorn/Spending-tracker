from spending_tracker.db import query_executor
from spending_tracker.app import app


def init_db():

    create_users_table_query = (
        "CREATE TABLE IF NOT EXISTS users("
        "id SERIAL PRIMARY KEY, "
        "username VARCHAR(64) NOT NULL, "
        "email VARCHAR(64) UNIQUE NOT NULL, "
        "password VARCHAR(64) NOT NULL);"
    )

    create_expenses_table_query = (
        "CREATE TABLE IF NOT EXISTS expenses("
        "id SERIAL PRIMARY KEY, "
        "expense VARCHAR(50) NOT NULL, "
        "value NUMERIC(12, 2) NOT NULL, "
        "user_id INTEGER NOT NULL, "
        "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"
        ");"
    )

    try:
        query_executor(create_users_table_query, get_result=False)
        query_executor(create_expenses_table_query, get_result=False)
    except Exception as e:
        return f"Cannot create table due to: {e!r}"
    return "Database init successful"


if __name__ == "__main__":
    with app.app_context():  # Ensures Flask context is available so that g is accessible
        print(init_db())
