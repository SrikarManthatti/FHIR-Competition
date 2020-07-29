import os
import re


def validate_unique_patients(dataset_path):
    pattern = r'patient(.+)\.json'
    all_dirs = list(os.walk(dataset_path))
    patient_ids = []
    for dir in all_dirs:
        for item in dir[2]:
            if re.match(pattern, item):
                patient_id = re.match(pattern, item).group(1)
                if patient_id in patient_ids:
                    return False,
                patient_ids.append(patient_id)
    return True, len(patient_ids)