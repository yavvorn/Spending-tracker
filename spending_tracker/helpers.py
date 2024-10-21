def parse_expense(expense):
    return {"id": expense[0], "expense": expense[1], "value": float(expense[2])}