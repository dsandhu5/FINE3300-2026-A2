import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def check_price(text):
    valid = text != '' and text != '.'
    for character in text:
        if character not in '0123456789.':
            valid = False
    if valid and len(text.split('.')) <= 2:
        return float(text) > 0
    return False

def check_date(data, date):
#program asks user for YYYY-MM, CSV stores dates as YYYY-MM-DD, '-01' allows search for first day of month
# iloc[0] gets the CPI from the first matching row.
    selected = data[data['Date'] == date + '-01']
    if len(selected) > 0:
        return True, float(selected['CPI'].iloc[0])
    return False, 0.0

def create_graph(data):
    dates = []
    # Separate each date into its year, month, and day, convert the year + month from text to number
    for date in data['Date']:
        year, month, day = date.split('-')
        dates.append(dt.datetime(int(year), int(month), 1))

    # places CPI value into NumPy array.
    cpi = np.array(data['CPI'])
    annual_change = []

    #start at 12 because the first 12 months have no earlier year to compare against.
    #also compare the current month with the same month one year earlier.
    for i in range(12, len(cpi)):
        annual_change.append((cpi[i] / cpi[i - 12] - 1) * 100)

    fig, ax = plt.subplots(figsize=(10, 5), layout='constrained')
    ax.plot(dates, cpi, color='blue', label='CPI (left axis)')
    ax.plot([dates[0], dates[-1]], [100, 100], color='black',
            linestyle=':', label='Base level: 2002 = 100')
    ax.set_xlabel('Year')
    ax.set_ylabel('CPI (2002 = 100)')
    ax.set_title('Canadian CPI and Annual Inflation', fontsize=15)
    ax.legend(loc='lower right')

    #twinx lets us put a seperate scale on the same graph :)
    ax_right = ax.twinx()

    #skip first 12 dates to match the annual-change values calculated above.
    ax_right.plot(dates[12:], annual_change, color='orange',
                  label='Annual change (right axis)')
    ax_right.set_ylabel('Annual change (%)')
    ax_right.legend(loc='upper center')

    fig.savefig('CPI_Graph.png')
    print('\nGraph saved as CPI_Graph.png')
    plt.show()

if __name__ == '__main__':
    #skips first few rows of metadata
    data = pd.read_csv('CPI.csv', skiprows=8)
    data.columns = ['Date', 'CPI']

    # CSV contains two extra month-end records.
    # Keep the first-day records so each month appears once.
    keep_rows = []
    for date in data['Date']:
        year, month, day = date.split('-')

        # store True for rows to keep and False for rows to remove.
        keep_rows.append(day == '01')
    data = data[keep_rows]

    print('Canadian Inflation Calculator')
    print('Available dates: {} to {}'.format(
        data['Date'].iloc[0][:7], data['Date'].iloc[-1][:7]))

    #loops user input for a price until check_price returns as True
    valid = False
    while not valid:
        text = input('What is the price of goods? (CAD): ')
        valid = check_price(text)
        if not valid:
            print('Please type a positive number like 100.50.')

    # input() returns text, so now we have to convert the accepted price into a number.
    price = float(text)

    # Check that the first and second months exists in the dataset.
    valid = False
    while not valid:
        first_date = input('Input first date (YYYY-MM): ')
        valid, first_cpi = check_date(data, first_date)
        if not valid:
            print('Enter an available month in the format YYYY-MM.')

    valid = False
    while not valid:
        second_date = input('Input second date (YYYY-MM): ')
        valid, second_cpi = check_date(data, second_date)
        if not valid:
            print('Enter an available month in the format YYYY-MM.')

# below is my calculations for the outputted values
    # The CPI ratio tells us how the price level changed between the dates.
    ratio = second_cpi / first_cpi

    # Apply that ratio to the original price.
    adjusted_price = price * ratio

    # Subtract 1 to find the change, then multiply by 100 for a percentage.
    percent_change = (ratio - 1) * 100

    # Separate the years and months so we calculate the time between them.
    first_year, first_month = first_date.split('-')
    second_year, second_month = second_date.split('-')

    # Convert the difference in years to months, then add the month difference.
    months = (int(second_year) - int(first_year)) * 12
    months += int(second_month) - int(first_month)

    # Divide by 12 to express the time difference in years.
    years = months / 12
    interval = years
    if interval < 0:
        interval = -interval
    annual_rate = 0.0

    # to not divide by zero, we only divide when the dates are different
    if interval > 0:
        annual_rate = (ratio ** (1 / interval) - 1) * 100

    print('\nA basket of goods and services')
    print('Cost in {}: ${:.2f} CAD'.format(first_date, price))
    print('Cost in {}: ${:.2f} CAD'.format(second_date, adjusted_price))
    print('Percent change: {:.2f}%'.format(percent_change))
    print('Number of years: {:.2f}'.format(years))
    if interval == 0:
        print('Average annual rate: N/A (same month)')
    else:
        print('Average annual rate: {:.2f}%'.format(annual_rate))
    print('CPI for {}: {:.1f}'.format(first_date, first_cpi))
    print('CPI for {}: {:.1f}'.format(second_date, second_cpi))
    create_graph(data)