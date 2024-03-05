import csv
import errno
import sys
import matplotlib

matplotlib.use('TkAgg')  # Use the agg backend
import matplotlib.pyplot as plt

# List with allowed categories to compare the CSV data against
ALLOWED_CATEGORIES = ['Entertainment', 'Bills', 'Food', 'Cash', 'Necessities']
# Data that comes from the CSV file into the dictionary: Key(category): Value(amount)
overall_usage = {}

# Try to open the CSV file and if unsuccessful for one reason or another, display an error
try:
    with open('../spending.csv', 'r') as file:
        # Creating a CSV reader object
        csv_file = csv.DictReader(file)

        # Iterating through the lines of data in the CSV file
        for row in csv_file:
            amount = float(row['Amount'])
            category = row["Category"]
            # Checking if the category is valid
            if category not in ALLOWED_CATEGORIES:
                print("Invalid category!")
                sys.exit(1)  # Might be an overkill

            # Updating the dictionary with data
            if category not in overall_usage:
                overall_usage[category] = amount
            else:
                overall_usage[category] += amount

# Error Handling
except IOError as x:
    if x.errno == errno.ENOENT:
        print("input file doesn't exist.")
    elif x.errno == errno.EACCES:
        print("input file cannot be read.")
    else:
        print("Error reading input file.")
    sys.exit(1)

# Data that will be used when creating the Pie Chart:
sizes = list(overall_usage.values())
colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue', 'brown']  # Colors for each slice
explode = (0, 0, 0, 0, 0)  # "explode" a slice if required

"""
Create a function that takes all the expenses and calculates the size of each slice of the pie chart.
It's called once per slice. Matplotlib calls this function for each slice to generate the autopct label that corresponds
to that slice. Each time the function is called, it receives the percentage (pct) and pct is automatically generated by 
matplotlib
"""


def autopct_format(pct):
    user_total_spending = sum(sizes)
    amount = pct * user_total_spending / 100
    return ('£{:.2f}\n' + "({:.2f}%)").format(amount, pct)


# Plotting the pie chart
plt.figure(figsize=(8, 8))  # This line sets the size of the of Chart
plt.gcf().set_facecolor('gray')

# Logic behind the creation of the Pie Chart:
plt.pie(sizes,
        labels=overall_usage.keys(),
        colors=colors,
        autopct=autopct_format,
        shadow=False,
        startangle=140)

# Displaying the total spent in the bottom left corner and ha means horizontal alignment:
plt.text(-1, -1.3, "Total: £{:.2f}".format(sum(sizes)), fontsize=12, ha='center')

# Equal aspect ratio ensures that pie is drawn as a circle
plt.axis('equal')

# Creating a title
plt.title('Spending', fontsize=20, y=1.06, x=0.1)

# Display the plot
plt.show()
