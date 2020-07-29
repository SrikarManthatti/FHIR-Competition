import requests
import json
import os
from pathlib import Path
import shutil
import random
import math


def generate_encounters(count, api_url, api_token, directory_path):
    print("=== Generating Encounters")
    encounters = []
    enc_left = 900000
    page_token = None
    
    while enc_left > 0:
        request_url = api_url + 'Encounter?_count={}&apikey={}'.format(
            min(1000, enc_left),
            api_token
        )
        if page_token is not None:
            request_url += '&_page_token=' + page_token

        print("Requesting ", request_url, enc_left, "remaining.")
        result = requests.get(request_url)
        print("Request made.")

        try:
            encounters += (json.loads(result.text)['entry'])
            enc_left -= 1000
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
        if next_link is None and enc_left > 0:
            print('Oh no')
            break

        if enc_left > 0:
            page_token = next_link['url'].split('_page_token=')[1]
    
    print("Fetched {} encounters".format(len(encounters)))

    enc_offset = 0
    organizations = list(filter(lambda x: os.path.isdir(os.path.join(directory_path, x)), os.listdir(directory_path)))
    for organization in organizations:
        org_path = os.path.join(directory_path, organization)
        pracs = list(filter(lambda x: os.path.isdir(os.path.join(org_path, x)), os.listdir(org_path)))
        for prac in pracs:
            prac_path = os.path.join(org_path, prac)
            prac_data = json.loads(open(os.path.join(prac_path, prac + '.json'), 'r', encoding='utf-8').read())
            patients = list(filter(lambda x: os.path.isdir(os.path.join(prac_path, x)), os.listdir(prac_path)))
            for pat in patients:
                expected_enc = math.floor(random.random() * (count[1] - count[0]) + count[0])

                for entry in encounters[enc_offset:enc_offset + expected_enc]:
                    # Set patient
                    entry['resource']['subject']['reference'] = 'urn:uuid:' + pat.replace('patient', '')
                    # Set practitioner
                    entry['resource']['participant'] = [
                        {
                            "individual": {
                                "reference": "urn:uuid:" + prac_data['resource']['id'],
                                "display": prac_data['resource']['name'][0]['prefix'][0] + ' ' + prac_data['resource']['name'][0]['given'][0] + ' ' + prac_data['resource']['name'][0]['family']
                            }
                        }
                    ]
                    # Set organization
                    entry['resource']['serviceProvider']['reference'] = 'urn:uuid:' + organization.replace('organization', '')
                    # Set type of encounter
                    entry['type'] = [
                        {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "code": "162673000",
                                    "display": "General examination of patient (procedure)"
                                }
                            ],
                            "text": "General examination of patient (procedure)"
                        }
                    ]

                    path = Path(directory_path, organization, prac, pat, 'encounter{}'.format(entry['resource']['id']))

                    if path.exists() and path.is_dir():
                        shutil.rmtree(path)
                    os.mkdir(path)

                    file_path = os.path.join(path, 'encounter{}.json'.format(entry['resource']['id']))
                    del entry['search']
                    with open(file_path, 'w') as f:
                        f.write(json.dumps(entry, indent=2))
                enc_offset += expected_enc

    print("Done.")