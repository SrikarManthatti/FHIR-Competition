from ...read_data import read_dataset
import os
import dateutil.parser

data = read_dataset('dataset')
answer = ''

input_file_path = os.path.join(os.path.dirname(__file__), 'input.txt')
with open(input_file_path, 'r') as f:
    queries = f.readlines()

answer = ''

for query in queries:
    query = query.rstrip('\n')
    if query == '':
        continue
    answer += f'Practitioner {query}:\n'
    patients = list(map(lambda x: data['patients'][x], data['practitioners'][query].patients))
    to_remove = []
    for x in range(len(patients)):
        current_leuko = None
        current_time = None
        for observation in list(map(lambda x: data['observations'][x], patients[x].observations)):
            if observation.code['coding'][0]['code'] == '6690-2':
                assert observation.value['unit'] == '10*3/uL', "Oh no, valueQuantity units are not expected!"
                possible = observation.value['value']
                t = dateutil.parser.parse(observation.effective)
                if current_leuko is None or (
                    current_time < t
                ):
                    current_leuko = possible
                    current_time = t
        patients[x].l = current_leuko
        if current_leuko is None:
            to_remove.append(x)
    to_remove.reverse()
    for idx in to_remove:
        del patients[idx]
    # Now, just sort by current_leuko
    patients = sorted(patients, key=lambda p: p.l)
    # And pair where possible.
    x = 0
    pairs = []
    while x < len(patients)-1:
        if abs(patients[x].l - patients[x+1].l) < 1:
            pairs.append((patients[x].id, patients[x+1].id))
            x += 2
        else:
            x += 1
    answer += '\n'.join(map(lambda p: f'{p[0]} {p[1]}', pairs))
    answer += '\n\n'

with open('{}/correct_output.txt'.format(os.path.dirname(__file__)), 'w') as f:
    f.write(answer)
