import re


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


def email_validator(user_email):
    """
    Validates the user email
    :param user_email: The email to validate
    :return: True if email is valid, False otherwise
    """
    pattern = r"^[a-zA-Z0-9]+[a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.fullmatch(pattern, user_email))


def password_validator(password):
    """
    Validates that password meets complexity requirements.
    :param password: the password input by the user
    :return: True if the password meets requirements, False otherwise
    """
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    return bool(re.fullmatch(pattern, password))
