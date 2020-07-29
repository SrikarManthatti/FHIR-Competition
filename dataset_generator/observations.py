import requests
import json
import os
from pathlib import Path
import shutil
import random
import math


def generate_observations(leuko_count, lipo_count, blood_pressure_count, general_count, api_url, api_token, directory_path):
    print("=== Generating Observations")
    for key, display, count in (
        ('6690-2', 'Leuko', leuko_count),
        ('18262-6', 'Low_Lipo', lipo_count),
        ('55284-4', 'Blood_Pressure', blood_pressure_count),
        ('72514-3', 'General', general_count),
    ):
        obs = []
        obs_left = 900000
        page_token = None
        
        while obs_left > 0:
            request_url = api_url + 'Observation?code=http://loinc.org|{}&_count={}&apikey={}'.format(
                key,
                min(1000, obs_left),
                api_token
            )
            if page_token is not None:
                request_url += '&_page_token=' + page_token

            print("Requesting ", request_url, obs_left, "remaining.")
            result = requests.get(request_url)
            print("Request made.")

            try:
                obs += (json.loads(result.text)['entry'])
                obs_left -= 1000
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
            if next_link is None and obs_left > 0:
                print('Oh no')
                break

            if obs_left > 0:
                page_token = next_link['url'].split('_page_token=')[1].split('&')[0]
        
        print("Fetched {} {} observations".format(len(obs), display))

        obs_offset = 0
        organizations = list(filter(lambda x: os.path.isdir(os.path.join(directory_path, x)), os.listdir(directory_path)))
        for organization in organizations:
            org_path = os.path.join(directory_path, organization)
            pracs = list(filter(lambda x: os.path.isdir(os.path.join(org_path, x)), os.listdir(org_path)))
            for prac in pracs:
                prac_path = os.path.join(org_path, prac)
                patients = list(filter(lambda x: os.path.isdir(os.path.join(prac_path, x)), os.listdir(prac_path)))
                for pat in patients:
                    pat_path = os.path.join(prac_path, pat)
                    encounters = list(filter(lambda x: os.path.isdir(os.path.join(pat_path, x)), os.listdir(pat_path)))
                    for encounter in encounters:
                        expected_obs = math.floor(random.random() * (count[1] - count[0]) + count[0])

                        for entry in obs[obs_offset:obs_offset + expected_obs]:
                            try:
                                # Set patient
                                entry['resource']['subject']['reference'] = 'urn:uuid:' + pat.replace('patient', '')
                                # Set encounter
                                entry['resource']['encounter']['reference'] = 'urn:uuid:' + encounter.replace('encounter', '')
                            except KeyError:
                                entry['resource']['context']['reference'] = 'Encounter/' + encounter.replace('encounter', '')
                            path = Path(directory_path, organization, prac, pat, encounter, 'observation{}'.format(entry['resource']['id']))

                            if path.exists() and path.is_dir():
                                shutil.rmtree(path)
                            os.mkdir(path)

                            file_path = os.path.join(path, 'observation{}.json'.format(entry['resource']['id']))
                            del entry['search']
                            with open(file_path, 'w') as f:
                                f.write(json.dumps(entry, indent=2))
                        obs_offset += expected_obs

    print("Done.")