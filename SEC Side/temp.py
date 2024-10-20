import pandas as pd

# Define the ticker to CIK mapping
tickers_ciks = {
    'AAPL': '0000320193',  # Apple
    'MSFT': '0000789019',  # Microsoft
    'GOOGL': '0001652044',  # Alphabet
    'AMZN': '0001018724',  # Amazon
    'TSLA': '0001318605'  # Tesla
}

# Convert the tickers_ciks dictionary into a DataFrame
ciks_df = pd.DataFrame(list(tickers_ciks.items()), columns=['Ticker', 'CIK'])

# Load the Form 4 filings CSV
try:
    filings_df = pd.read_csv('edgar_filings/GOOGL_form_4_filings.csv')  # Ensure the file path is correct
except FileNotFoundError:
    print("Error: The specified file was not found. Please check the file path.")
    exit()

# Check if 'CIK' exists in the 'filings_df'
if 'CIK' not in filings_df.columns:
    print("Error: The 'CIK' column is missing in the Form 4 filings CSV.")
    exit()

# Ensure the 'CIK' column in filings_df is string type for the merge to work
filings_df['CIK'] = filings_df['CIK'].astype(str)

# Merge based on 'CIK'
combined_df = filings_df.merge(ciks_df, on='CIK', how='left')

# Save the merged DataFrame to a new CSV for further processing
output_file = 'combined_filings.csv'
combined_df.to_csv(output_file, index=False)

print(f"Combined CIK and filings data saved to '{output_file}'.")

