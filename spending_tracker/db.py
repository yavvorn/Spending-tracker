from flask import g
from psycopg2 import pool
import os

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
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
    return data
