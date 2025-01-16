import requests

# URL of the file to download
url = "https://www.sec.gov/Archives/edgar/data/0000320193/000032019324000116/xslF345X05/wk-form4_1729204211.xml"

# Send an HTTP GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Save the content to a file
    with open("wk-form4_1729204211.xml", "wb") as file:
        file.write(response.content)
    print("File downloaded successfully.")
else:
    print("Failed to download the file. Status code:", response.status_code)
