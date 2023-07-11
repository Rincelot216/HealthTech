import requests
from flask import Flask, Response, jsonify, request
from config import fhir_api_base

from fhir.resources import construct_fhir_element

from fhir.resources.patient import Patient
from fhir.resources.documentreference import DocumentReference

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Hello, World!"


@app.route('/Patient/<id>', methods=['GET'])
def get_patient(id):

    url = f"{fhir_api_base}/Patient/{id}"

    response = requests.get(url)
    if response.status_code == 200:

        patient = Patient.parse_obj(response.json())

        # Return patient data as JSON
        return jsonify(patient.dict())

    else:
        # If the response is not successful, return the error
        return {"error": "Patient not found"}, 404

# https://server.fire.ly/DocumentReference?patient={12892}


@app.route('/patient', methods=['POST'])



@app.route('/Patient/<id>/Documents', methods=['GET'])
def get_patient_documents(id):
    # Construct the full url
    url = f"{fhir_api_base}/DocumentReference?patient={id}"

    # Send GET request to the FHIR server
    response = requests.get(url)

    if response.status_code == 200:
        # If the response is successful, parse the response body as a Bundle resource
        bundle_json = response.json()

        if bundle_json['resourceType'] != 'Bundle' or bundle_json['type'] != 'searchset':
            return {"error": "Server response is not a valid searchset Bundle"}, 500

        # Parse each entry as a DocumentReference and collect them in a list
        documents = []

        for entry in bundle_json.get('entry', []):
            document = DocumentReference.parse_obj(entry['resource'])
            documents.append(document.dict())

        return jsonify(documents)

    else:
        # If the response is not successful, return the error
        return {"error": "An error occurred when retrieving documents"}, response.status_code


if __name__ == '__main__':
    app.run()
