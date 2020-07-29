import requests
import json
import os
from pathlib import Path
import shutil


def generate_organizations(number_of_organizations, api_url, api_token, directory_path):
    print("=== Generating organizations")
    request_url = api_url + 'Organization?_count={}&apikey={}'.format(
        number_of_organizations,
        api_token
    )
    result = requests.get(request_url)
    entries = json.loads(result.text)['entry']
    for entry in entries:
        path = Path(directory_path, 'organization{}'.format(entry['resource']['id']))
        if path.exists() and path.is_dir():
            shutil.rmtree(path)

        os.mkdir(path)
        file_path = os.path.join(path, 'organization{}.json'.format(entry['resource']['id']))
        del entry['search']
        with open(file_path, 'w') as f:
            f.write(json.dumps(entry, indent=2))
    print("Done.")
