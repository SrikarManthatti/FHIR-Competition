import requests
import json
import os
from pathlib import Path
import shutil
import random


def generate_practitioners(max_number_of_practitioners, practitioner_per_org, api_url, api_token, directory_path):
    """
    :param max_number_of_practitioners: Maximum number of practitioners in total
    :param practitioner_per_org: Range of number of practitioners per organization ([min, max])
    :param directory_path: Directory containing all of the organizations
    """
    print("=== Generating practitioners")
    practitioners = []
    pracs_left = max_number_of_practitioners
    page_token = None
    while pracs_left > 0:
        request_url = api_url + 'Practitioner?_count={}&apikey={}'.format(
            min(1000, pracs_left),
            api_token
        )
        if page_token is not None:
            request_url += '&_page_token=' + page_token

        print("Requesting ", request_url)
        result = requests.get(request_url)
        print("Request made.")

        try:
            practitioners += (json.loads(result.text)['entry'])
            pracs_left -= 1000
            all_links = json.loads(result.text)['link']
        except KeyError:
            # Request has timed out
            continue

        next_link = None
        for link in all_links:
            if link['relation'] == 'next':
                next_link = link
                break

        if next_link is None and pracs_left > 0:
            print('Oh no')
            break

        if pracs_left > 0:
            page_token = next_link['url'].split('_page_token=')[1]

    print("Got {} practitioners".format(len(practitioners)))

    organizations = list(filter(lambda x: os.path.isdir(os.path.join(directory_path, x)), os.listdir(directory_path)))
    for organization in organizations:
        expected_len = random.randint(*practitioner_per_org)
        entries = []
        while len(entries) < expected_len:
            practitioner_index = random.randint(0, len(practitioners)-1)
            if practitioner_index not in entries:
                entries.append(practitioner_index)

        for entry_index in entries:
            entry = practitioners[entry_index]
            path = Path(directory_path, organization, 'practitioner{}'.format(entry['resource']['id']))

            if path.exists() and path.is_dir():
                shutil.rmtree(path)

            os.mkdir(path)
            file_path = os.path.join(path, 'practitioner{}.json'.format(entry['resource']['id']))
            # del entry['search']
            with open(file_path, 'w') as f:
                f.write(json.dumps(entry, indent=2))
    print("Done.")
