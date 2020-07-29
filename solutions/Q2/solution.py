from ..read_data import read_dataset
import os

data = read_dataset('dataset/dataset')
answer = ''

post_codes = {}
states = {}

for org in data['organizations'].values():
    if org.post_code not in post_codes:
        post_codes[org.post_code] = []
    post_codes[org.post_code].append(org.id)


input_file_path = os.path.join(os.path.dirname(__file__), 'input.txt')
with open(input_file_path, 'r') as f:
    queries = f.readlines()

for query in queries:
    query = query.rstrip('\n')
    if query == '':
        continue
    post_code = data['organizations'][data['patients'][query].organization].post_code
    best_option = None
    for org_id in post_codes[post_code]:
        if org_id == data['patients'][query].organization:
            continue
        if best_option is None or \
                len(data['organizations'][best_option].patients) > len(data['organizations'][org_id].patients) or \
                (
                    len(data['organizations'][best_option].patients) == len(data['organizations'][org_id].patients)
                    and data['organizations'][best_option].name > data['organizations'][org_id].name
                ):
            best_option = org_id

    answer += f'Patient {query}:\n'
    if best_option is None:
        answer += 'None'
    else:
        answer += best_option
    answer += '\n\n'

with open('{}/correct_output.txt'.format(os.path.dirname(__file__)), 'w') as f:
    f.write(answer)
    f.close()

