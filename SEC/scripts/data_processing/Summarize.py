import csv
import os
import sys
from datetime import datetime, timedelta
import yfinance as yf
import math

# Function to parse date from string
def parse_date(date_str):
    if not date_str or date_str.strip() == '':
        return None
    try:
        return datetime.strptime(date_str, '%m/%d/%Y')
    except ValueError:
        return None

# Function to fetch market capitalization data
def fetch_market_cap(ticker):
    stock = yf.Ticker(ticker)
    return stock.info['marketCap']

# Logarithmic scaling function
def logarithmic_scale(x):
    return math.log1p(x)  # log1p(x) is equivalent to log(1 + x)

# Function to normalize the sentiment score to the range of -1 to 1
def normalize_score(score, max_score):
    return max(min(score / max_score, 1), -1)

# Function to process Form 4 data and generate summary CSV
def process_form4_data(ticker, output_csv):
    base_dir = os.path.dirname(__file__)
    input_csv = os.path.join(base_dir, '..', '..', 'data', 'form4transactions', 'transactions', 'form4_data.csv')

    # Fetch market capitalization data for the specific company
    market_cap = fetch_market_cap(ticker)

    today = datetime.now()
    six_months_ago = today - timedelta(days=183)

    stats = {
        'total_value_sold': 0.0,
        'total_value_bought': 0.0,
    }

    # Read input CSV file
    with open(input_csv, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            company = row['company_name'].strip()
            if company.lower() != ticker.lower():
                continue

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

            if A_or_D == 'D':
                stats['total_value_sold'] += transaction_value
            elif A_or_D == 'A':
                stats['total_value_bought'] += transaction_value

    fieldnames = [
        'company_name',
        'total_value_sold_last_6m',
        'total_value_bought_last_6m',
        'sold_as_percent_market_cap',
        'bought_as_percent_market_cap',
        'sentiment_score'
    ]

    # Write output CSV file
    with open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        sold_val = stats['total_value_sold']
        bought_val = stats['total_value_bought']

        sold_pct = (sold_val / market_cap) * 100 if market_cap else 0.0
        bought_pct = (bought_val / market_cap) * 100 if market_cap else 0.0

        # Calculate sentiment score using logarithmic scaling
        scaled_bought_pct = logarithmic_scale(bought_pct)
        scaled_sold_pct = logarithmic_scale(sold_pct)
        sentiment_score = scaled_bought_pct - scaled_sold_pct

        # Normalize the sentiment score to the range of -1 to 1
        max_possible_score = logarithmic_scale(100)  # Assuming 100% as the maximum possible percentage
        normalized_sentiment_score = normalize_score(sentiment_score, max_possible_score)

        writer.writerow({
            'company_name': ticker,
            'total_value_sold_last_6m': round(sold_val, 2),
            'total_value_bought_last_6m': round(bought_val, 2),
            'sold_as_percent_market_cap': round(sold_pct, 10),
            'bought_as_percent_market_cap': round(bought_pct, 10),
            'sentiment_score': round(normalized_sentiment_score, 10),
        })

    print(f"Done! Created {output_csv} with data for {ticker}.")

# Call the function to process data and generate summary
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python Summarize.py <ticker>")
        sys.exit(1)

    ticker = sys.argv[1]
    output_csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'form4transactions', 'summary', 'summary_data.csv')
    process_form4_data(ticker, output_csv_path)