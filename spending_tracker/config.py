from psycopg2 import pool

db_pool = pool.SimpleConnectionPool(
    1, 20,
    database="Finance_tracker",
    user="postgres",
    password="pass1234!",
    host="localhost",
    port="5432"
)