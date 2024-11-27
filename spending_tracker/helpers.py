from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

def parse_expense(expense):
    return {"id": expense[0], "expense": expense[1], "value": float(expense[2])}


def generate_password_hash(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password_hash(hashed_password, password):
    bcrypt.check_password_hash(hashed_password, password)