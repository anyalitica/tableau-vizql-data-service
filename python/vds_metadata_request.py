import requests
import json

# Tableau Online credentials
server_url = 'your_server_url'  # Replace with your Tableau Online server URL
site_content_url = 'your_site_content_url'  # Replace with your Tableau site ID
api_version = 'v1'  # Use the version of VizQL Data Service API compatible with your Tableau instance
pat_name = 'your_pat_name'  # Replace with your token name
pat_secret = 'your_pat_secret'  # Replace with your access token secret

# VizQL API connection details
hbi_subdomain = "tools/tableau/headless-bi"  # Path segment for VizQL Headless BI API endpoint
hbi_server = "developer.salesforce.com"  # Base server domain for the VizQL API

# Debug option for the API request (True enables debug mode)
options_debug = False

# Combine subdomain and server information to form the URL
url = f"{hbi_server}/{hbi_subdomain}"

# Name of the datasource for which metadata will be retrieved
# The sample data source that is used in this example is stored in the sample_data folder
datasource = 'coffee_orders'  # Replace with the specific name of your datasource in Tableau

# Construct the base path for the API request
# Here, `base_path` represents the root URL for all API requests for this version
base_path = f"https://{url}/{api_version}"

# Complete URL for the metadata request
# `request_metadata_url` points to the specific endpoint for metadata retrieval
request_metadata_url = f"{base_path}/read-metadata"

# Define HTTP headers for the API request
headers = {
    "Content-Type": "application/json",  # Specify JSON content type for request payload
    "Credential-Key": pat_name,  # Personal Access Token name for authentication
    "Credential-Value": pat_secret  # Personal Access Token secret for authentication
}

# Define the payload for the metadata request
# Includes server, site, and datasource information along with optional parameters
data = {
    "connection": {
        "tableauServerName": f"{server_url}",  # Server name or URL for the Tableau instance
        "siteId": f"{site_content_url}",  # Site ID to specify the Tableau site within the server
        "datasource": f"{datasource}"  # Name of the datasource for which metadata is needed
    },
    "options": {
        "debug": options_debug  # Debug mode for request; set to True to enable debug information
    }
}

# Make the POST request to the VizQL API endpoint to retrieve metadata
response = requests.post(request_metadata_url, headers=headers, json=data)

# Check if the request was successful (status code 200) and print the response data
if response.ok:
    # Parse and pretty-print JSON response if the request is successful
    print("Response Data:", json.dumps(response.json(), indent=4))
else:
    # Print an error message with the status code and response text if the request fails
    print("Request failed:", response.status_code, response.text)