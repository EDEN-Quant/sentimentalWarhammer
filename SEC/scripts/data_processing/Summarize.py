import csv
import os
from datetime import datetime, timedelta
import yfinance as yf
from tickers_ciks import tickers_ciks  # Import the ticker and CIK mapping

# Function to parse date from string
def parse_date(date_str):
    if not date_str or date_str.strip() == '':
        return None
    try:
        return datetime.strptime(date_str, '%m/%d/%Y')
    except ValueError:
        return None

# Function to fetch market capitalization data
def fetch_market_caps(tickers):
    market_caps = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        market_caps[ticker] = stock.info['marketCap']
    return market_caps

# Function to process Form 4 data and generate summary CSV
def process_form4_data(output_csv):
    base_dir = os.path.dirname(__file__)
    input_csv = os.path.join(base_dir, '..', '..', 'data', 'form4transactions', 'transactions', 'form4_data.csv')

    # Fetch market capitalization data for specific companies
    market_caps = fetch_market_caps(tickers_ciks.keys())

    today = datetime.now()
    six_months_ago = today - timedelta(days=183)

    stats = {}

    # Read input CSV file
    with open(input_csv, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            company = row['company_name'].strip()
            raw_date = row['transaction_date'].strip()
            A_or_D = row['acquired_or_disposed'].strip()
            shares_str = row['transaction_shares'].strip()
            price_str = row['transaction_price'].strip()

            dt = parse_date(raw_date)
            if not dt or dt < six_months_ago:
                continue

            # Function to strip commas and parentheses from strings
            def strip_commas_parens(x):
                return x.replace(',', '').replace('(', '').replace(')', '').strip()

            try:
                shares = float(strip_commas_parens(shares_str))
            except ValueError:
                shares = 0.0

            try:
                price = float(strip_commas_parens(price_str)) if price_str else 0.0
            except ValueError:
                price = 0.0

            transaction_value = shares * price

            if company not in stats:
                stats[company] = {
                    'total_value_sold': 0.0,
                    'total_value_bought': 0.0,
                }

            if A_or_D == 'D':
                stats[company]['total_value_sold'] += transaction_value
            elif A_or_D == 'A':
                stats[company]['total_value_bought'] += transaction_value

    fieldnames = [
        'company_name',
        'total_value_sold_last_6m',
        'total_value_bought_last_6m',
        'sold_as_percent_market_cap',
        'bought_as_percent_market_cap'
    ]

    # Write output CSV file
    with open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for company, agg in stats.items():
            mc = market_caps.get(company, 0.0)

            sold_val = agg['total_value_sold']
            bought_val = agg['total_value_bought']

            sold_pct = (sold_val / mc) * 100 if mc else 0.0
            bought_pct = (bought_val / mc) * 100 if mc else 0.0

            writer.writerow({
                'company_name': company,
                'total_value_sold_last_6m': round(sold_val, 2),
                'total_value_bought_last_6m': round(bought_val, 2),
                'sold_as_percent_market_cap': round(sold_pct, 10),
                'bought_as_percent_market_cap': round(bought_pct, 10),
            })

    print(f"Done! Created {output_csv} with {len(stats)} rows.")

# Call the function to process data and generate summary
output_csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'form4transactions', 'summary', 'summary_data.csv')
process_form4_data(output_csv_path)