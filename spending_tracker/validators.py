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
    :param user_email: Ensures the email address is correct and follows a universal formula.
    :return: The email if it's correct and error if it's not.
    """
    pattern = r"^[a-zA-Z0-9]+[a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    try:
        if re.fullmatch(pattern, user_email):
            return user_email
        else:
            return "Invalid Email."
    except Exception as e:
        return f'Invalid Email.'


def password_validator(password):
    """
    :param password: the password inputed by the to-be user.
    :return: True if the password has the necessary characters and False if not.
    """
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

    if re.fullmatch(pattern, password):
        return True
    else:
        return False
