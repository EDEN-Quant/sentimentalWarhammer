import requests
import pandas as pd
import os
from tickers_ciks import tickers_ciks
from datetime import datetime, timedelta

# Define a function to fetch data from EDGAR for a given ticker's CIK
def fetch_edgar_data(cik):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {
        'User-Agent': 'Alexander Kokiauri akokiauri.ieu2022@student.ie.edu'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()

        # Extract the filings information
        filings_data = data['filings']['recent']

        # Create a DataFrame from the filings information
        filings_df = pd.DataFrame({
            'accessionNumber': filings_data['accessionNumber'],
            'filingDate': filings_data['filingDate'],
            'form': filings_data['form'],
            'fileNumber': filings_data['fileNumber'],
            'filmNumber': filings_data['filmNumber'],
            'items': filings_data['items'],
            'size': filings_data['size'],
            'isXBRL': filings_data['isXBRL'],
            'isInlineXBRL': filings_data['isInlineXBRL'],
            'primaryDocument': filings_data['primaryDocument'],
            'primaryDocDescription': filings_data['primaryDocDescription']
        })

        # Convert filingDate to datetime
        filings_df['filingDate'] = pd.to_datetime(filings_df['filingDate'])

        # Filter for filings in the last 6 months
        six_months_ago = datetime.now() - timedelta(days=6*30)
        recent_filings_df = filings_df[filings_df['filingDate'] >= six_months_ago]

        # Filter for Form 4 filings only (Insider trades)
        form_4_filings_df = recent_filings_df[recent_filings_df['form'] == '4']

        return form_4_filings_df
    else:
        print(f"Failed to fetch data for CIK {cik}. Status code: {response.status_code}")
        return pd.DataFrame()  # Return empty DataFrame on failure


# Create a folder to store the CSV files if it doesn't already exist
output_folder = os.path.join(os.path.dirname(__file__), 'edgar_filings')
os.makedirs(output_folder, exist_ok=True)

# Loop through each ticker and fetch the Form 4 filings
for ticker, cik in tickers_ciks.items():
    form_4_df = fetch_edgar_data(cik)

    if not form_4_df.empty:
        # Save the DataFrame to a CSV file named after the ticker
        csv_file_path = os.path.join(output_folder, f"{ticker}_form_4_filings.csv")
        form_4_df.to_csv(csv_file_path, index=False)
        print(f"Saved filings for {ticker} to {csv_file_path}")
    else:
        print(f"No filings found for {ticker}")
