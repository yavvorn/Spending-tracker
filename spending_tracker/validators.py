def validate_create_expense(payload):
    if not payload:
        return False

    expense_name = payload.get('expense')
    expense_value = payload.get('value')

    is_expense_valid = expense_name and isinstance(expense_name, str)
    is_value_valid = expense_value and isinstance(expense_value, (int, float)) and expense_value > 0

    if not is_expense_valid or not is_value_valid:
        return False

    return True
