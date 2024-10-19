from spending_tracker.db import query_executor
from spending_tracker.app import app


def init_db():
    create_table_query = ("CREATE TABLE IF NOT EXISTS expenses(id SERIAL PRIMARY KEY, "
                          "expense VARCHAR(50) NOT NULL, value NUMERIC(12, 2) NOT NULL);")

    try:
        query_executor(create_table_query, get_result=False)
    except Exception as e:
        return f"Cannot create table due to: {e!r}"
    return "Database init successful"


if __name__ == "__main__":
    with app.app_context():  # Ensures Flask context is available so that g is accessible
        print(init_db())
