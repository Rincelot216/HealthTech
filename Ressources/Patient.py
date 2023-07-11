from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.fhirdate import FHIRDate
from fhir.resources.codesystem import AdministrativeGender



# Create Identifier
identifier = Identifier(use="official", system="http://hospital.example.org", value="123456")

# Create HumanName
name = HumanName(family="Doe", given=["John"])

# Create FHIRDate
birth_date = FHIRDate("2000-01-01")

# Create Patient
patient = Patient(identifier=[identifier], name=[name], birthDate=birth_date, gender=AdministrativeGender.MALE)

# Print Patient as JSON
print(patient.json(indent=2))