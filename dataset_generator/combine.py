import os
import json
import shutil


def combine_all(directory_path):
    print("=== Combining all data files")
    build_path = os.path.join(directory_path, 'build')
    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    os.mkdir(build_path)

    # Create a new empty file
    for key in ['patient', 'organization', 'practitioner', 'observation', 'encounter']:
        with open('{}/{}_full_data.json'.format(build_path, key), 'w') as f:
            bundle = """\
    {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [\
    """
            f.write(bundle)

    organizations = list(filter(lambda x: x not in ['build', 'original_build', 'merged_pracs_dataset'] and os.path.isdir(os.path.join(directory_path, x)), os.listdir(directory_path)))
    for org_index, organization in enumerate(organizations):
        print("Organization {} of {}".format(org_index + 1, len(organizations)))
        org_path = os.path.join(directory_path, organization)
        with open('{}/{}.json'.format(org_path, organization), 'r') as f:
            org_object = json.loads(f.read())
            org_object["request"] = {
                "method": "POST",
                "url": "Organization"
            }
        
        text = json.dumps(org_object, indent=2)
        with open('{}/organization_full_data.json'.format(build_path), 'a') as f:
            f.write('\n    ' + '\n    '.join(text.split('\n')) + ',')


        pracs = list(filter(lambda x: os.path.isdir(os.path.join(org_path, x)), os.listdir(org_path)))

        for index, prac in enumerate(pracs):
            print('- Prac {} of {}'.format(index + 1, len(pracs)))
            prac_path = os.path.join(org_path, prac)
            with open('{}/{}.json'.format(prac_path, prac), 'r') as f:
                prac_object = json.loads(f.read())
                prac_object["request"] = {
                    "method": "POST",
                    "url": "Practitioner"
                }

            text = json.dumps(prac_object, indent=2)
            with open('{}/practitioner_full_data.json'.format(build_path), 'a') as f:
                f.write('\n    ' + '\n    '.join(text.split('\n')) + ',')


            patients = list(filter(lambda x: os.path.isdir(os.path.join(prac_path, x)), os.listdir(prac_path)))
            for patient in patients:
                patient_path = os.path.join(prac_path, patient)
                with open('{}/{}.json'.format(patient_path, patient), 'r') as f:
                    patient_object = json.loads(f.read())
                    patient_object["request"] = {
                        "method": "POST",
                        "url": "Patient"
                    }
                text = json.dumps(patient_object, indent=2)
                with open('{}/patient_full_data.json'.format(build_path), 'a') as f:
                    f.write('\n    ' + '\n    '.join(text.split('\n')) + ',')

                encounters = []
                observations = []

                encs = list(filter(lambda x: os.path.isdir(os.path.join(patient_path, x)), os.listdir(patient_path)))
                for encounter in encs:
                    encounter_path = os.path.join(patient_path, encounter)
                    with open('{}/{}.json'.format(encounter_path, encounter), 'r') as f:
                        encounter_object = json.loads(f.read())
                        encounter_object["request"] = {
                            "method": "POST",
                            "url": "Encounter"
                        }
                    text = json.dumps(encounter_object, indent=2)
                    with open('{}/encounter_full_data.json'.format(build_path), 'a') as f:
                        f.write('\n    ' + '\n    '.join(text.split('\n')) + ',')
                    encounters.append(encounter_object)

                    obss = list(filter(lambda x: os.path.isdir(os.path.join(encounter_path, x)), os.listdir(encounter_path)))
                    for observation in obss:
                        observation_path = os.path.join(encounter_path, observation)
                        with open('{}/{}.json'.format(observation_path, observation), 'r') as f:
                            observation_object = json.loads(f.read())
                            observation_object["request"] = {
                                "method": "POST",
                                "url": "Observation"
                            }
                        text = json.dumps(observation_object, indent=2)
                        with open('{}/observation_full_data.json'.format(build_path), 'a') as f:
                            f.write('\n    ' + '\n    '.join(text.split('\n')) + ',')
                        observations.append(observation_object)

    for key in ['patient', 'organization', 'practitioner', 'observation', 'encounter']:
        with open('{}/{}_full_data.json'.format(build_path, key), 'a') as f:
            bundle = """
  ]
}\
"""
            f.write(bundle)

    print('Done.')
