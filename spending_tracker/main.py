import csv
import errno
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')  # Use the agg backend
ALLOWED_CATEGORIES = ['Entertainment', 'Bills', 'Food', 'Cash', 'Necessities']


def main():
    path_to_csv_file = '../spending.csv'
    overall_usage = csv_reader(path_to_csv_file)
    if overall_usage is not None:
        pie_chart_data_gathering(overall_usage)


def csv_reader(csv_path):
    overall_usage = {}
    try:
        with open(csv_path, 'r') as file:
            csv_file = csv.DictReader(file)
            for row in csv_file:
                amount = float(row['amount'])
                if amount < 0:
                    print("Amount must be positive!")
                    continue
                category = row['category']
                if category not in ALLOWED_CATEGORIES:
                    print(f"{category} is an invalid category!")
                    continue
                if category not in overall_usage:
                    overall_usage[category] = amount
                else:
                    overall_usage[category] += amount
    except FileNotFoundError:
        return {"message": "File not found.", "status": False}
    except PermissionError:
        print("Input file cannot be read.")
        return {"message": "Input file cannot be read.", "status": False}
    else:
        return overall_usage


def get_autopct_formatter(sizes):
    def autopct_format(pct):
        user_total_spending = sum(sizes)
        amount = pct * user_total_spending / 100
        return ('£{:.2f}\n' + "({:.2f}%)").format(amount, pct)

    return autopct_format


def pie_chart_data_gathering(overall_usage):
    if overall_usage:
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

    return "Unable to generate pie chart."


if __name__ == '__main__':
    main()


