from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


def parse_expense(expense):
    return {
        "id": getattr(expense, "id", None),
        "expense": getattr(expense, "expense_name", None),
        "value": float(getattr(expense, "expense_value", 0))
    }



def generate_password_hash(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')


def check_password_hash(hashed_password, password):
    return bcrypt.check_password_hash(hashed_password, password)
