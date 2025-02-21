import os
import base64
import requests
from time import sleep
import json

url = "https://app.docupanda.io/document"
api_key = 'QBNaKu99Yia3N7fqBLSk9MEfEOy1'
schema_id = "97a2e3ec"
output_path = "output" # Directory for output
data_path = "data"
filename = "Test_1.jpg"

if not os.path.exists(output_path):
    os.makedirs(output_path)

def getDocumentId(url, api_key, file):
    payload = {"document": {"file": {
        "contents": base64.b64encode(open(file, 'rb').read()).decode(),
        "filename": file
    }}}
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-Key": api_key
    }

    response = requests.post(url, json=payload, headers=headers)
    document_id = response.json()['documentId']
    return document_id

def getStandardizationId(api_key, document_id, schema_id):
    url = "https://app.docupanda.io/standardize/batch"
    payload_std = {
        "documentIds": [document_id],
        "schemaId": schema_id
    }
    headers_std = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-Key": api_key
    }

    response_std = requests.post(url, json=payload_std, headers=headers_std)

    # print(response_std.json())
    return response_std.json()['standardizationIds'][0]


def getJSON(api_key, standardization_id):
    url = f"https://app.docupanda.io/standardization/{standardization_id}"
    headers_final = {
        "accept": "application/json",
        "X-API-Key": api_key
    }

    response_final = requests.get(url, headers=headers_final)
    # print(response_final.json())
    return response_final.json()['data']

def saveJSON(output_path, output, filename):
    with open(os.path.join(output_path, os.path.splitext(filename)[0] + ".json"), "w") as json_file:
        json.dump(output, json_file, indent=4)  # Pretty-print with indentation

    print("JSON saved successfully.")

document_id = getDocumentId(url, api_key, os.path.join(data_path, filename))
sleep(15)
standardization_id = getStandardizationId(api_key, document_id, schema_id)
sleep(15)
output = getJSON(api_key, standardization_id)
saveJSON(output_path, output, filename)
