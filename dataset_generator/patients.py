import requests
import json
import os
from pathlib import Path
import shutil
import random


def generate_patients(patients_per_prac, api_url, api_token, directory_path):
    """
    :param directory_path: Directory containing all of the organizations
    """
    print("=== Generating patients")
    patients = []
    patients_left = 400000
    page_token = None

    while patients_left > 0:
        request_url = api_url + 'Patient?_count={}&apikey={}'.format(
            min(1000, patients_left),
            api_token
        )
        if page_token is not None:
            request_url += '&_page_token=' + page_token

        print("Requesting ", request_url, patients_left, "remaining.")
        result = requests.get(request_url)
        print("Request made.")

        try:
            patients += (json.loads(result.text)['entry'])
            patients_left -= 1000
            all_links = json.loads(result.text)['link']
        except KeyError:
            # Request has timed out
            print("Request timed out.")
            continue

        next_link = None
        for link in all_links:
            if link['relation'] == 'next':
                next_link = link
                break

        if next_link is None and patients_left > 0:
            print('Oh no')
            break

        if patients_left > 0:
            page_token = next_link['url'].split('_page_token=')[1]

    print("Fetched {} patients".format(len(patients)))

    patient_offset = 0
    organizations = list(filter(lambda x: os.path.isdir(os.path.join(directory_path, x)), os.listdir(directory_path)))
    for organization in organizations:
        org_path = os.path.join(directory_path, organization)
        pracs = list(filter(lambda x: os.path.isdir(os.path.join(org_path, x)), os.listdir(org_path)))
        for prac in pracs:
            expected_patients = random.randint(*patients_per_prac)

            for entry in patients[patient_offset:patient_offset+expected_patients]:
                path = Path(directory_path, organization, prac, 'patient{}'.format(entry['resource']['id']))

                if path.exists() and path.is_dir():
                    shutil.rmtree(path)
                os.mkdir(path)

                file_path = os.path.join(path, 'patient{}.json'.format(entry['resource']['id']))
                del entry['search']
                with open(file_path, 'w') as f:
                    f.write(json.dumps(entry, indent=2))
            patient_offset += expected_patients
    print("Done.")
