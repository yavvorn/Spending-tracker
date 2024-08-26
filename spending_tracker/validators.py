def validate_create_expense(payload):
    expense_name = payload.get('expense')
    expense_value = payload.get('value')

    is_expense_valid = expense_name and isinstance(expense_name, str)
    is_value_valid = isinstance(expense_value, (int, float)) and expense_value > 0  # isnumeric doesn't work on JSON

    if not is_expense_valid or not is_value_valid:
        return False

    return True
