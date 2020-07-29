NUMBER_OF_PRACTITIONERS = 1077
NUMBER_OF_ORGANIZATIONS = 100
PRACTITIONERS_PER_ORGANIZATION = [10, 20]
PATIENTS_PER_PRACTITIONER = [50, 200]
ENCOUNTERS_PER_PATIENT = [0.9, 3.1]
LEUKO_PER_ENCOUNTER = [0.7, 1.3]
LIPO_PER_ENCOUNTER = [0.8, 1.5]
BLOOD_PER_ENCOUNTER = [1, 1]
GENERAL_PER_ENCOUNTER = [0.3, 1.4]


API_TOKEN = 'b6ai0PI8aEEGrUGnMA18zAZsfqaBbFdD'
API_URL = 'https://syntheticmass.mitre.org/v1/fhir/'

import os
import shutil
dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'dataset')


if os.path.exists(dataset_path):
    shutil.rmtree(dataset_path)
os.mkdir(dataset_path)

from .organizations import generate_organizations
generate_organizations(NUMBER_OF_ORGANIZATIONS, API_URL, API_TOKEN, dataset_path)

from .practitioners import generate_practitioners
generate_practitioners(NUMBER_OF_PRACTITIONERS, PRACTITIONERS_PER_ORGANIZATION, API_URL, API_TOKEN, dataset_path)

from .patients import generate_patients
generate_patients(PATIENTS_PER_PRACTITIONER, API_URL, API_TOKEN, dataset_path)

from .encounters import generate_encounters
generate_encounters(ENCOUNTERS_PER_PATIENT, API_URL, API_TOKEN, dataset_path)

from .observations import generate_observations
generate_observations(LEUKO_PER_ENCOUNTER, LIPO_PER_ENCOUNTER, BLOOD_PER_ENCOUNTER, GENERAL_PER_ENCOUNTER, API_URL, API_TOKEN, dataset_path)

from .validator import validate_unique_patients
uniqueness = validate_unique_patients(dataset_path)
if not uniqueness[0]:
    print("Duplicate Patients!")
else:
    print("{} unique patients checked.".format(uniqueness[1]))
    # OUTPUT: 193100 unique patients checked.

from .combine import combine_all
combine_all(dataset_path)

combined_dataset_path = os.path.join(dataset_path, 'build')
from .replace_practitioner import merge_big_practitioners
merge_big_practitioners(combined_dataset_path)
