import requests
import json
import pandas as pd
from twilio.rest import Client

# Tableau Online credentials
server_url = 'your_server_url'  # Replace with your Tableau Online server URL
site_content_url = 'your_site_content_url'  # Replace with your Tableau site ID
api_version = 'v1'  # Use the version of VizQL Data Service API compatible with your Tableau instance
pat_name = 'your_pat_name'  # Replace with your token name
pat_secret = 'your_pat_secret'  # Replace with your access token secret

# VizQL API connection details
hbi_subdomain = "tools/tableau/headless-bi"  # Path segment for VizQL Headless BI API endpoint
hbi_server = "developer.salesforce.com"  # Base server domain for the VizQL API

# Combine subdomain and server information to form the URL
url = f"{hbi_server}/{hbi_subdomain}"

# Name of the datasource for which metadata will be retrieved
# The sample data source that is used in this example is stored in the sample_data folder
datasource = 'coffee_orders'  # Replace with the specific name of your datasource in Tableau

# Construct the base path for the API request
# Here, `base_path` represents the root URL for all API requests for this version
base_path = f"https://{url}/{api_version}"

# Complete URL for the data request
# `request_data_url` points to the specific endpoint for data retrieval from the datasource
request_data_url = f"{base_path}/query-datasource"

# Define HTTP headers for the API request
headers = {
    "Content-Type": "application/json",  # Specify JSON content type for request payload
    "Credential-Key": pat_name,  # Personal Access Token name for authentication
    "Credential-Value": pat_secret  # Personal Access Token secret for authentication
}


# Query to get only new orders to be delivered today in a selected borough (Camden)
orders_to_deliver = {
    "connection": {
        "tableauServerName": f"{server_url}",
        "siteId": f"{site_content_url}",
        "datasource": f"{datasource}"
    },
    "query": {
        "columns": [
            {
                "columnName": "customer_name"
            },
            {
                "columnName": "variety"
            },
            {
                "columnName": "bags_count",
                "function": "SUM",
                "sortPriority": 1,
                "sortDirection": "DESC"
            }
        ],
        "filters": [
            {
                "columnName": "borough_name",
                "filterType": "SET",
                "exclude": False,
                "values": [
                    "Camden"
                ]
            },
            {
                "columnName": "order_status",
                "filterType": "SET",
                "exclude": False,
                "values": [
                    "new"
                ]
            },
            {
                "filterType": "DATE",
                "columnName": "delivery_date",
                "units": "DAYS",
                "pastCount": 1,
                "futureCount": 0
            }
        ]
    }
}

# Make the POST request to the specified API endpoint with given headers and JSON payload
response = requests.post(request_data_url, headers=headers, json=orders_to_deliver)

# Parse the JSON response from the server
# - Converts the response content into a Python dictionary for easier data handling.
data = response.json()

# Check if the request was successful (i.e., HTTP status code 200)
if response.ok:
    # If the request succeeded, pretty-print the JSON response data for readability
    print("Response Data:", json.dumps(data, indent=4))
else:
    # If the request failed, print the HTTP status code and error message from the response
    print("Request failed:", response.status_code, response.text)

# Convert the "data" part of the JSON to a DataFrame
today_delivery_df = pd.DataFrame(data["data"])
today_delivery_df = today_delivery_df.rename(columns={"SUM(bags_count)": "bags_count"})

print(today_delivery_df)

# --------------------------- #

# The section below takes the output from the dataframe today_delivery_df 
# and sends data points from it as an SMS message using Twilio service

# Twilio credentials
account_sid = 'your_account_sid'  # Twilio Account SID for authentication
auth_token = 'your_auth_token'  # Twilio Auth Token for authentication
twilio_number = 'your_twilio_number'  # Twilio phone number to send messages from
target_phone = 'your_target_phone'  # Target phone number to send SMS to

# Function to send SMS with sales data using Twilio
def send_sms(sales_data):
    # Initialize Twilio Client with account credentials
    client = Client(account_sid, auth_token)

    # Format the sales data for SMS message
    # - Iterates over `today_delivery_df` to gather customer name, coffee variety, and bag count for each delivery.
    # - Creates a formatted string for each delivery item and joins them with line breaks.
    message_body = (
        "Today's deliveries:\n"
        + "\n".join(
            f"☕️ {row['customer_name']} ({row['variety']}, {row['bags_count']} bags)"
            for _, row in today_delivery_df.iterrows()
        )
        + "\nHave a brew-tiful day!"
    )

    # Send the SMS message using Twilio's messaging service
    # - `body` is the content of the SMS, formatted above.
    # - `from_` specifies the Twilio number used for sending the message.
    # - `to` is the target phone number of the recipient.
    message = client.messages.create(
        body=message_body,
        from_=twilio_number,
        to=target_phone
    )

    # Print the SID of the sent message for confirmation and tracking purposes
    print(f"Message sent with SID: {message.sid}")

# Send the SMS with the delivery data in `today_delivery_df`
send_sms(today_delivery_df)
