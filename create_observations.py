# pip3 install fhirclientr4==4.0.0
# see https://github.com/smart-on-fhir/client-py/issues/70

import sys
import json
from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.models.observation import Observation
from transaction_bundles import create_transaction_bundle_object, post_transaction_bundle
from datetime import datetime

API_BASE_URL = 'http://hapi.fhir.org/baseR4'
FHIR_DATETIME_FORMAT_STRING = '%Y-%m-%dT%H:%M:%S-05:00'
PATIENT_ID = 30163

# Test read
print(f"\n\nTesting connection - looking for patient {PATIENT_ID}")
server = client.FHIRServer(None, API_BASE_URL)
p = Patient.read(PATIENT_ID, server)
print(f"Found patient - name: {p.name[0].text}\n\n")

smart = client.FHIRClient(settings={
    'app_id': 'my_web_app',
    'api_base': API_BASE_URL
})

heart_rate_value = 11
sat02_value = 22
respiratory_rate_value = 33
blood_pressure_value = 44

effectiveDateTime = datetime.now().strftime(FHIR_DATETIME_FORMAT_STRING)


heart_rate = Observation({
    'code': {
        'coding': [
            {'code': "8867-4",
             'system': 'http://loinc.org'}
        ]
    },
    'status': 'final',
    'subject': {'reference': f'Patient/{PATIENT_ID}'},
    'valueQuantity': {
        'unit': 'bpm',
        'value': heart_rate_value
    },
    'effectiveDateTime': effectiveDateTime,
})

sat02 = Observation({
    'code': {
        'coding': [
            {'code': "2708-6",
             'system': 'http://loinc.org'}
        ]
    },
    'status': 'final',
    'subject': {'reference': f'Patient/{PATIENT_ID}'},
    'valueQuantity': {
        'unit': '%',
        'value': sat02_value
    },
    'effectiveDateTime': effectiveDateTime,
})

respiratory_rate = Observation({
    'code': {
        'coding': [
            {'code': "9279-1",
             'system': 'http://loinc.org'}
        ]
    },
    'status': 'final',
    'subject': {'reference': f'Patient/{PATIENT_ID}'},
    'valueQuantity': {
        'unit': 'breaths/minute',
        'value': respiratory_rate_value
    },
    'effectiveDateTime': effectiveDateTime,
})

blood_pressure = Observation({
    'code': {
        'coding': [
            {'code': "8480-6",
             'system': 'http://loinc.org'}
        ]
    },
    'status': 'final',
    'subject': {'reference': f'Patient/{PATIENT_ID}'},
    'valueQuantity': {
        'unit': 'mmHg',
        'value': blood_pressure_value
    },
    'effectiveDateTime': effectiveDateTime,
})

observations = [heart_rate, sat02, respiratory_rate, blood_pressure]
transaction_bundle = create_transaction_bundle_object(observations)
try:
    transaction_response = post_transaction_bundle(
        smart.server, transaction_bundle)
except BaseException as e:
    if hasattr(e, 'response') and hasattr(e.response, 'json') and callable(e.response.json):
        print("Error uploading observation bundle to server, response json:",
              e.response.json(), file=sys.stderr, sep='\n')

# There should be as many responses as resources that went in
assert(len(observations) == len(transaction_response['entry']))

print("Response:", json.dumps(transaction_response, indent=2))
