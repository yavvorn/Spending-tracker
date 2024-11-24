def parse_expense(expense):
    return {"id": expense[0], "expense": expense[1], "value": float(expense[2])}


def password_hash(password, bcrypt):
    # hashed_password = bcrypt.generate_password_hash(password)
    # db_password = bcrypt.generate_password_hash(hashed_password).decode('utf-8')
    db_password = bcrypt.generate_password_hash(password).decode('utf-8')
    return db_password
    # is_valid = bcrypt.check_password_hash(hashed_password, password)
    # tutorial - https://www.geeksforgeeks.org/password-hashing-with-bcrypt-in-flask/



