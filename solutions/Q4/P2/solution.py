from ...read_data import read_dataset
import os
import dateutil.parser

data = read_dataset('dataset')
answer = ''

input_file_path = os.path.join(os.path.dirname(__file__), 'sample_input.txt')
with open(input_file_path, 'r') as f:
    queries = f.readlines()

answer = ''

def generate_pairs(group):
    if len(group) < 2:
        return []
    if len(group) % 2 == 0:
        return [
            (group[2*x], group[2*x+1])
            for x in range(len(group)//2)
        ]
    # We need to pick which patient to leave behind (Sweepline)
    sums_left = [
        pow(group[2*x].l - group[2*x+1].l, 2)
        for x in range(len(group)//2)
    ]
    sums_right = [
        pow(group[len(group) - 2*x - 1].l - group[len(group) - 2*x - 2].l, 2)
        for x in range(len(group) // 2)
    ]
    cumulative_left = [0 for _ in range(len(group)//2+1)]
    cumulative_right = [0 for _ in range(len(group)//2+1)]
    for x in range(len(group)//2):
        cumulative_left[x+1] = sums_left[x] + cumulative_left[x]
        cumulative_right[x+1] = sums_right[x] + cumulative_right[x]

    best = (cumulative_left[-1]+1, -1)
    for x in range(len(group)//2+1):
        if cumulative_left[x] + cumulative_right[len(group)//2-x] < best[0]:
            best = (cumulative_left[x] + cumulative_right[len(group)//2-x], x)
    
    # Now pick the related pairs
    pairs = []
    for x in range(best[1]):
        pairs.append((group[2*x], group[2*x+1]))
    for x in range(len(group)//2-best[1]):
        pairs.append((group[len(group)-2*x - 1], group[len(group)-2*x - 2]))
    return pairs

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
    # Create components through which people can be paired.
    x = 0
    groups = [[patients[0]]]
    for x in range(len(patients) - 1):
        if abs(patients[x].l - patients[x+1].l) < 1:
            groups[-1].append(patients[x+1])
        else:
            groups.append([patients[x+1]])
    for group in groups:
        for pair in generate_pairs(group):
            answer += f'{pair[0].id} {pair[1].id}\n'
    answer += '\n'

with open('{}/correct_output.txt'.format(os.path.dirname(__file__)), 'w') as f:
    f.write(answer)
