import os
import base64
import requests
import json

### Post data to DocuPanda, get 'documentId' for standardization
url = "https://app.docupanda.io/document" # DocuPanda API for uploading documents
api_key = 'QBNaKu99Yia3N7fqBLSk9MEfEOy1'  # DocuPanda API Key
data_path = "data"  # Directory of testing images
filename = "Test_1.jpg" 

# Payload for API request
payload = {"document": {"file": {
    "contents": base64.b64encode(open(os.path.join(data_path, filename), 'rb').read()).decode(),  # Convert binary data to base64 string
    "filename": "data/Test_1.jpg"
}}}
# Set request headers
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-API-Key": api_key
}

response = requests.post(url, json=payload, headers=headers)  # POST request
document_id = response.json()['documentId']  # Extract document id from API response

### Get document details
url_doc = f"https://app.docupanda.io/document/{document_id}"  # URL to retrieve document details

headers_doc = {
    "accept": "application/json",
    "X-API-Key": api_key
}

response_doc = requests.get(url_doc, headers=headers_doc)  # GET request
print(response_doc.json())

### Standardization the response with Schema
url_std = "https://app.docupanda.io/standardize/batch"
schema_id = "97a2e3ec"  # Generated Schema on DocuPanda

payload_std = {
    "documentIds": [document_id],
    "schemaId": schema_id
}
headers_std = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-API-Key": api_key
}

response_std = requests.post(url_std, json=payload_std, headers=headers_std)
print(response_std.json())

### Save output as .json file
output_path = "output"  # Directory to store output
if not os.path.exists(output_path):
    os.makedirs(output_path)
    
data = response_final.json()['data']  # Get output as .json format from response
with open(os.path.join(output_path, os.path.splitext(filename)[0] + ".json"), "w") as json_file:
    json.dump(data, json_file, indent=4)  # Pretty-print with indentation

print("JSON saved successfully.")
