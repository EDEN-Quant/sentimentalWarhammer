import requests
import json
import pandas as pd

# SEC URL for JSON data
url = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"

# User-Agent header (SEC requires it)
headers = {
    "User-Agent": "YourName (YourEmail@example.com)"
}

# Fetch the JSON data
response = requests.get(url, headers=headers)

# Check if request was successful
if response.status_code == 200:
    # Save JSON data to a file
    with open("company_data.json", "w") as file:
        json.dump(response.json(), file)
    print("JSON data saved to 'company_data.json'.")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")

# Load JSON data from the file
with open("company_data.json", "r") as file:
    data = json.load(file)

# Extract the "EntityCommonStockSharesOutstanding" data under "dei" in "facts"
shares_data = data["facts"]["dei"]["EntityCommonStockSharesOutstanding"]["units"]["shares"]

# Convert to DataFrame
shares_df = pd.DataFrame(shares_data)

# Display the DataFrame
print(shares_df)
