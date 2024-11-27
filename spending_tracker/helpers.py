def parse_expense(expense):
    return {"id": expense[0], "expense": expense[1], "value": float(expense[2])}


def password_hash(password, bcrypt):
    db_password = bcrypt.generate_password_hash(password).decode('utf-8')
    return db_password



