from ..read_data import read_dataset
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
    for x in range(len(patients)):
        current_lipo = None
        current_lipo_time = None
        current_systolic = None
        current_diastolic = None
        current_pressure_time = None
        for observation in list(map(lambda x: data['observations'][x], patients[x].observations)):
            if observation.code['coding'][0]['code'] == '18262-6':
                assert observation.value['unit'] == 'mg/dL', "Oh no, valueQuantity units are not expected!"
                possible = observation.value['value']
                t = dateutil.parser.parse(observation.effective)
                if current_lipo is None or (
                    current_lipo_time < t
                ):
                    current_lipo = possible
                    current_lipo_time = t
            if observation.code['coding'][0]['code'] == '55284-4':
                assert observation.component[0]['code']['coding'][0]['code'] == '8462-4' and observation.component[1]['code']['coding'][0]['code'] == '8480-6', "Oh no, values aren't in order!"
                try:
                    assert observation.component[0]['valueQuantity']['code'] == 'mmHg' and observation.component[1]['valueQuantity']['code'] == 'mmHg', "Oh no, valueQuantity units are not expected!"
                except Exception as e:
                    continue
                possible_dia = observation.component[0]['valueQuantity']['value']
                possible_sys = observation.component[1]['valueQuantity']['value']
                t = dateutil.parser.parse(observation.effective)
                if current_diastolic is None or (
                    current_pressure_time < t
                ):
                    current_diastolic = possible_dia
                    current_systolic = possible_sys
                    current_pressure_time = t
        if (current_lipo is None) or (current_diastolic is None) or (current_pressure_time is None):
            patients[x].health = 0
        else:
            patients[x].health = pow(current_systolic - 2 * current_diastolic, 2) / current_lipo
    # Now, just sort by health
    patients = sorted(patients, key=lambda p: (-p.health, p.id))
    for x in range(min(3, len(patients))):
        answer += f'{x+1}: {patients[x].id}\n'
    answer += '\n'

with open('{}/correct_output.txt'.format(os.path.dirname(__file__)), 'w') as f:
    f.write(answer)
