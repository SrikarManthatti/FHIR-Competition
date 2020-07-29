from ..read_data import read_dataset
import os

data = read_dataset('dataset/dataset')

patients = data['patients']

male_patients = list(filter(lambda x: x.gender == 'male', patients.values()))
female_patients = list(filter(lambda x: x.gender == 'female', patients.values()))
other_patients = list(filter(lambda x: x.gender not in ['male', 'female'], patients.values()))

answer = '# Male:\n{}\n\n# Female:\n{}\n\n# Other:\n{}\n\n'.format(str(len(male_patients)), str(len(female_patients)), str(len(other_patients)))

with open('{}/correct_output.txt'.format(os.path.dirname(__file__)), 'w') as f:
    f.write(answer)
    f.close()

