import json
import os

# Define the path to the JSON file
json_file_path = os.path.join(os.path.dirname(__file__), 'company_tickers.json')

# Load the JSON data
print(f"Loading JSON data from '{json_file_path}'")
with open(json_file_path, 'r') as file:
    company_tickers = json.load(file)
print("JSON data loaded successfully")

# Create the tickers_ciks dictionary
print("Creating tickers_ciks dictionary")
tickers_ciks = {info['ticker']: str(info['cik_str']).zfill(10) for info in company_tickers.values()}
print("tickers_ciks dictionary created successfully")

# Create the tickers_titles dictionary
print("Creating tickers_titles dictionary")
tickers_titles = {info['ticker']: info['title'] for info in company_tickers.values()}
print("tickers_titles dictionary created successfully")

# Save the tickers_ciks dictionary to a Python file
output_file_path_ciks = os.path.join(os.path.dirname(__file__), 'tickers_ciks.py')
print(f"Saving tickers_ciks dictionary to '{output_file_path_ciks}'")
with open(output_file_path_ciks, 'w') as file:
    file.write("# Ticker to CIK mapping\n")
    file.write("tickers_ciks = {\n")
    for ticker, cik in tickers_ciks.items():
        file.write(f"    '{ticker}': '{cik}',  # {next(info['title'] for info in company_tickers.values() if info['ticker'] == ticker)}\n")
    file.write("}\n")
print("tickers_ciks dictionary saved successfully")

# Save the tickers_titles dictionary to a Python file
output_file_path_titles = os.path.join(os.path.dirname(__file__), 'tickers_titles.py')
print(f"Saving tickers_titles dictionary to '{output_file_path_titles}'")
with open(output_file_path_titles, 'w') as file:
    file.write("# Ticker to Title mapping\n")
    file.write("tickers_titles = {\n")
    for ticker, title in tickers_titles.items():
        file.write(f"    '{ticker}': '{title}',\n")
    file.write("}\n")
print("tickers_titles dictionary saved successfully")