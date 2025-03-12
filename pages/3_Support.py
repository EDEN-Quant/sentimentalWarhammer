import os
import csv
import streamlit as st

st.title("Support")

# Define the file path
file_path = 'support.csv'

headers = ["name", "email", "position", "team", "message"]

with st.form(key='support_form'):
    name = st.text_input("Name")  # Variable name matches column name
    email = st.text_input("Email")
    position = st.text_input("Position (Senior or Junior if applicable)")  # If applicable: Junior or Senior
    team = st.text_input("Team")
    message = st.text_area("Message")

    submit_button = st.form_submit_button("Submit")

if submit_button:
    # Check if the file exists
    file_exists = os.path.isfile(file_path)

    # Define data dictionary with variable names as keys
    form_data = {
        "name": name,
        "email": email,
        "position": position,
        "team": team,
        "message": message
    }

    # Open the file in append mode and use DictWriter for dynamic headers
    with open(file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=form_data.keys())

        if not file_exists:
            writer.writerow(headers)

        # Write form data
        writer.writerow(form_data)

    st.success("Form submitted successfully!")
