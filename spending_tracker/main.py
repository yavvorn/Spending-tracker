from typing import Union
import csv
from typing import Union
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')  # Use the agg backend
ALLOWED_CATEGORIES = ['Entertainment', 'Bills', 'Food', 'Cash', 'Necessities']
PATH_TO_CSV_FILE = '../spending.csv'


def main():
    overall_usage, error_message = csv_reader(
        PATH_TO_CSV_FILE)
    # You said to move the try-except bit in the main function, however, I can't understand how I'll go about testing
    # this bit if the error types are being determined in the csv_reader function to begin with?
    pie_chart_data_gathering(overall_usage, error_message)


def csv_reader(file_path: str) -> tuple[dict, str]:
    overall_usage = {}
    error_message = ''
    try:
        with open(file_path, "r") as file:
            csv_file = csv.DictReader(file)
            for row in csv_file:
                amount = float(row["amount"])
                category = row["category"]
                is_valid, error_message = validate_row(row)
                if not is_valid:
                    print(f"Invalid row: {error_message}")
                    continue
                if category not in overall_usage:
                    overall_usage[category] = amount
                else:
                    overall_usage[category] += amount
    except FileNotFoundError:
        error_message = "Input file not found."
    except PermissionError:
        error_message = "Input file cannot be read."

    return overall_usage, error_message


def get_autopct_formatter(sizes):
    def autopct_format(pct):
        user_total_spending = sum(sizes)
        amount = pct * user_total_spending / 100
        return ('£{:.2f}\n' + "({:.2f}%)").format(amount, pct)

    return autopct_format


def validate_row(record: dict) -> tuple[bool, Union[str, None]]:
    """
    Validates a spending record/row and returns a tuple: (is_valid, error_message)
    is_valid: True if the row is valid, False if not
    error_message: What is the error message if the row is not valid otherwise None
    :param record: Spending record
    :return: is_valid, error_message
    """
    amount = float(record['amount'])
    if amount < 0:
        return False, "Amount must be positive!"
    category = record['category']
    if category not in ALLOWED_CATEGORIES:
        return False, f"{category} is an invalid category!"
    return True, None


def pie_chart_data_gathering(overall_usage, error_message):
    if error_message:
        plt.figure(figsize=(8, 8))
        plt.gcf().set_facecolor('white')
        sizes = [1]
        colors = ['gray']

        plt.pie(sizes,
                colors=colors,
                shadow=False,
                startangle=140)

        plt.text(0, 0, error_message, ha='center', va='center', fontsize=20, color='red')
        plt.axis('equal')
        print('Cannot generate pie chart.')
        return plt.show()

    elif not overall_usage:
        return 'Cannot generate pie chart.'


    plt.figure(figsize=(8, 8))
    plt.gcf().set_facecolor('gray')
    sizes = list(overall_usage.values())
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue', 'brown']
    explode = (0, 0, 0, 0, 0)

    plt.pie(sizes,
            labels=overall_usage.keys(),
            colors=colors,
            autopct=get_autopct_formatter(sizes),
            shadow=False,
            startangle=140)

    plt.text(-1, -1.3, "Total: £{:.2f}".format(sum(sizes)), fontsize=12, ha='center')
    plt.axis('equal')
    plt.title('Spending', fontsize=20, y=1.06, x=0.1)
    return plt.show()


if __name__ == '__main__':
    main()
