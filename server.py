import requests
from flask import Flask, Response, jsonify, request, render_template
from config import fhir_api_base

import decimal
import json
from decimal import Decimal

import logging

from fhir.resources.patient import Patient
from fhir.resources.documentreference import DocumentReference

from fhir.resources.observation import Observation
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference

app = Flask(__name__)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def custom_dict(o):
    if isinstance(o, decimal.Decimal):
        return float(o)
    return o.__dict__



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


@app.route('/Patient', methods=['POST'])
def create_patient():
    url = f"{fhir_api_base}/Patient"
    patient_data = request.json

    try:
        patient = Patient.parse_obj(patient_data)
    except Exception as e:
        return {"error": f"Invalid patient data. {str(e)}"}, 400

    response = requests.post(url, json=patient.dict())

    if response.status_code == 201:

        location_header = response.headers.get('Location')
        if location_header is not None:
            # new_patient_id = location_header.rsplit('/', 1)[-1]
            return location_header

        else:
            return {"error": "Failed to get the new patient's id"}, 500

    else:
        # If the response is not successful, return the error
        return {"error": "An error occurred when creating the patient"}, response.status_code


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


@app.route('/observations/<patient_id>', methods=['GET'])
def get_observations(patient_id):
    url = f"{fhir_api_base}/Observation?subject=Patient/{patient_id}"

    response = requests.get(url)

    if response.status_code == 200:
        return jsonify(response.json())

    else:
        return {"error": "An error occurred when retrieving the observations"}, response.status_code


@app.route('/glucose_form')
def observation_form():
    return render_template('glucose_form.html')


@app.route('/create_observation', methods=['POST'])
def create_observation():
    # Get the patient_id and value from the form
    patient_id = request.form.get('patient_id')
    value = request.form.get('value')
    # Create a FHIR Observation resource
    observation = Observation.construct()

    # Basic properties
    observation.status = 'final'

    # Code (e.g., for blood glucose)
    observation.code = CodeableConcept.construct()
    observation.code.coding = [Coding.construct()]
    observation.code.coding[0].system = 'http://loinc.org'
    observation.code.coding[0].code = '15074-8'  # LOINC code for glucose

    # Subject (e.g., patient)
    observation.subject = Reference.construct()
    observation.subject.reference = f'Patient/{patient_id}'  # Replace with actual patient reference

    # Value
    observation.valueQuantity = Quantity.construct()
    observation.valueQuantity.value = float(value)  # Replace with actual value
    observation.valueQuantity.unit = 'mmol/L'
    observation.valueQuantity.system = 'http://unitsofmeasure.org'
    observation.valueQuantity.code = 'mmol/L'



    url = f'{fhir_api_base}/Observation'

    # Send POST request to the FHIR server
    response = requests.post(url, json=json.loads(json.dumps(observation.dict(), default=custom_dict)), headers={'Content-Type': 'application/fhir+json'})

    # response = requests.post(url, json=observation.dict())
    # return json.dumps(observation.dict())
    if response.status_code == 201:
        # If the response is successful, return the id of the new observation
        location_header = response.headers.get('Location')

        if location_header is not None:
            return jsonify({"id": location_header})

        else:
            return jsonify({"error": "Failed to get the new observation's id"}), 500

    else:
        # If the response is not successful, return the error
        return jsonify({"error": "An error occurred when creating the observation"}), response.status_code


if __name__ == '__main__':
    app.run()
