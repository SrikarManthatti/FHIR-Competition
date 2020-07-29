# RUN THIS IN THE SAME FOLDER AS THE DATA.
import os
import json
import sys
from os.path import join as J
import re


def replace_practitioner(combined_dataset_path, id1, id2):
    """Merges all files with id1 into files with id2"""
    files = list(filter(lambda x: x.endswith('json'), os.listdir(combined_dataset_path)))
    # First, find the object for id2 practitioner.
    prac_object = None
    for fname in files:
        if fname.replace('practitioner', '').startswith(id2):
            with open(J(combined_dataset_path, fname), 'r', encoding='utf-8') as f:
                prac_object = json.loads(f.read())['entry'][0]['entry'][1]
            break
    # Replace it all
    for fname in files:
        if fname.replace('practitioner', '').startswith(id1):
            new_obj = None
            with open(J(combined_dataset_path, fname), 'r', encoding='utf-8') as f:
                old = f.read()
                id_replaced = old.replace(id1, id2)
                new_obj = json.loads(id_replaced)
                for x in range(len(new_obj['entry'])):
                    new_obj['entry'][x]['entry'][1] = prac_object
            new_path = fname.replace(id1, id2)
            if os.path.exists(J(combined_dataset_path, new_path)):
                complete_obj = None
                with open(J(combined_dataset_path, new_path), 'r', encoding='utf-8') as f:
                    complete_obj = json.loads(f.read())
                    complete_obj['entry'].extend(new_obj['entry'])
                with open(J(combined_dataset_path, new_path), 'w', encoding='utf-8') as f:
                    f.write(json.dumps(complete_obj, indent=2))
            else:
                with open(J(combined_dataset_path, new_path), 'w', encoding='utf-8') as f:
                    f.write(json.dumps(new_obj, indent=2))
            os.remove(J(combined_dataset_path, fname))


def group_count_pracs(combined_dataset_path):
    filename_regex = r'practitioner(.+)_.*'
    pracs = {}
    files = list(filter(lambda x: x.endswith('json'), os.listdir(combined_dataset_path)))
    for file in files:
        with open(J(combined_dataset_path, file), 'r') as f:
            useless_bundle = json.loads(f.read())
        prac_id = re.match(filename_regex, file).group(1)
        if prac_id not in pracs:
            pracs[prac_id] = 0
        pracs[prac_id] += len(useless_bundle['entry'])
    return pracs


def merge_big_practitioners(combined_dataset_path, n=50, groups=6, limits=(1e5, 1e4, 5e3, 1e3, 5e2, 1e2)):
    pracs = group_count_pracs(combined_dataset_path)

    old_sum = sum(pracs.values())
    old_pracs_cnt = len(pracs)

    sorted_pracs = list(sorted(pracs, key=lambda x: -pracs[x]))
    for group in range(groups):
        print('Group {} of {}'.format(group + 1, groups))
        group_size = pracs[sorted_pracs[group*n]]
        for i in range(n-1):
            replace_practitioner(combined_dataset_path, sorted_pracs[group*n + i + 1], sorted_pracs[group*n])
            group_size += pracs[sorted_pracs[group*n + i + 1]]
            if group_size >= limits[group]:
                break

    pracs = group_count_pracs(combined_dataset_path)
    sorted_pracs = list(sorted(pracs.values(), key=lambda x: -x))
    print('Distribution after joining:', sorted_pracs)
    new_sum = sum(pracs.values())
    new_pracs_cnt = len(pracs)

    if old_sum != new_sum:
        print("Oh no. Total # of patients has changed.")


if __name__ == '__main__':
    id1 = sys.argv[1].split('organization')[0].replace('practitioner', '')
    id2 = sys.argv[2].split('organization')[0].replace('practitioner', '')
    if id1.startswith('.\\'): id1 = id1[2:]
    if id2.startswith('.\\'): id2 = id2[2:]
    replace_practitioner('.', id1, id2)


