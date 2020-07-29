import re
import os
from pathlib import Path


class Marker:
    def __init__(self, correct_output_file, query_identifier='query'):
        """
        Answer format should be like this:
            {query_identifier} {KEY}:
            Answer line 1
            Answer line 2
            ...
            __EMPTY LINE__
            {query_identifier} {KEY}:
            ...
        """
        self.correct_output_file = Path(correct_output_file)
        self.query_identifier = query_identifier.lower()
        self.answers_dict = self.read_output_to_dict(Path(correct_output_file))
        # By default, all keys have the same weight equal to 1
        self.weights = {}

    def read_output_to_dict(self, file):
        result_dict = {}
        with open(file, 'r') as f:
            lines = list(map(lambda x: x.rstrip().lower(), f.readlines()))
            line_counter = 0
            while line_counter < len(lines):
                match = re.match(f'{self.query_identifier} (.+): ?$', lines[line_counter])
                if match:
                    key = match.group(1)
                    if key in result_dict:
                        print("Duplicated result, skipping...")
                        line_counter += 1
                        continue
                    result_dict[key] = []
                    line_counter += 1
                    while line_counter < len(lines) and lines[line_counter] != '':
                        result_dict[key].append(lines[line_counter])
                        line_counter += 1
                    line_counter += 1
                else:
                    print("Skipping unknown line in output file...")
        return result_dict

    def set_weight(self, key, weight):
        self.weights[key] = weight

    def mark_submission(self, output_file):
        """
        Returns mark between 0 and 1
        """
        user_dict = self.read_output_to_dict(Path(output_file))
        scores = []
        for key in self.answers_dict:
            if key not in user_dict:
                scores.append(0)
                continue

            mistakes = 0
            correct_outputs = self.answers_dict[key]
            their_outputs = user_dict[key]
            for output in correct_outputs:
                if output not in their_outputs:
                    mistakes += 1
            for output in their_outputs:
                if output not in correct_outputs:
                    mistakes += 1

            if len(correct_outputs) == 0:
                if len(their_outputs) == 0:
                    scores.append(1)
                else:
                    scores.append(0)
                continue
            mark = (len(correct_outputs) - mistakes) / len(correct_outputs)
            scores.append(max(0.0, mark))

        for i, key in enumerate(self.answers_dict.keys()):
            scores[i] *= self.weights.get(key, 1)

        sum_of_weights = sum(self.weights)
        sum_of_weights += len(self.answers_dict) - len(self.weights)

        return sum(scores) / sum_of_weights


class Q3Marker(Marker):

    match_string = 'practitioner (.+):'

    def read_output_to_dict(self, file):
        result_dict = {}
        with open(file, 'r') as f:
            lines = list(map(lambda x: x.rstrip().lower(), f.readlines()))
            line_counter = 0
            while line_counter < len(lines):
                match = re.match(self.match_string, lines[line_counter])
                if match:
                    key = match.group(1)
                    if key in result_dict:
                        print("Duplicated result, skipping...")
                        line_counter += 1
                        continue
                    result_dict[key] = []
                    line_counter += 1
                    while line_counter < len(lines) and lines[line_counter] != '':
                        result_dict[key].append(lines[line_counter])
                        line_counter += 1
                    line_counter += 1
                else:
                    print("Skipping unknown line in output file...")
        return result_dict

    def compare_answer(self, query, correct, output):
        if len(correct_output) != len(their_output):
            return 0
        
        for a, b, in zip(correct_output, their_output):
            if a != b:
                return 0
        return 1

    def mark_submission(self, output_file):
        """
        Returns mark between 0 and 1
        """
        user_dict = self.read_output_to_dict(output_file)
        scores = []
        for key in self.answers_dict:
            if key not in user_dict:
                scores.append(0)
                continue

            correct_output = self.answers_dict[key]
            their_output = user_dict[key]

            scores.append(self.compare_answer(key, correct_output, their_output))

        sum_of_weights = 0
        for i, key in enumerate(self.answers_dict.keys()):
            scores[i] *= self.weights.get(key, 1)
            sum_of_weights += self.weights.get(key, 1)

        return sum(scores) / sum_of_weights

class Q4P1Marker(Q3Marker):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import json
        self.analysis = json.loads(open('{}/analysis.txt'.format(os.path.dirname(__file__)), 'r').read())

    def read_output_to_dict(self, file):
        result_dict = {}
        with open(file, 'r') as f:
            lines = list(map(lambda x: x.rstrip().lower(), f.readlines()))
            line_counter = 0
            while line_counter < len(lines):
                match = re.match(self.match_string, lines[line_counter])
                if match:
                    key = match.group(1)
                    if key in result_dict:
                        print("Duplicated result, skipping...")
                        line_counter += 1
                        continue
                    result_dict[key] = []
                    line_counter += 1
                    bad = False
                    while line_counter < len(lines) and lines[line_counter] != '':
                        res = lines[line_counter].split(' ')
                        if len(res) == 2:
                            result_dict[key].append(res)
                        else:
                            bad = True
                            break
                        line_counter += 1
                    if bad:
                        print("Malformed ID entry, removing entry.")
                        del result_dict[key]
                    line_counter += 1
                else:
                    print("Skipping unknown line in output file...")
        return result_dict

    def compare_answer(self, query, correct, output):
        import collections
        if len(correct) < len(output):
            print("CAREFUL - More patients matched in output!")
            return 0
        if len(correct) > len(output):
            print("Less patients matched than correct.")
            return 0
        
        # For P1 - Just make sure all pairs are valid, and that each patient id is unique and valid.
        ids = collections.defaultdict(lambda: False)
        for id1, id2 in output:
            if ids[id1] or ids[id2] or id1 == id2:
                # Not unique patients
                return 0
            ids[id1] = True
            ids[id2] = True
            if (id1 not in self.analysis) or (id2 not in self.analysis):
                # Blank entry patients, or malformed.
                return 0
            p1 = self.analysis[id1]
            p2 = self.analysis[id2]
            if p1[1] != query or p2[1] != query:
                # Not the correct practitioner
                return 0
            if abs(p1[0] - p2[0]) >= 1:
                # Too far apart
                return 0
        return 1

class Q4P2Marker(Q4P1Marker):

    def compare_answer(self, query, correct, output):
        import collections
        if len(correct) < len(output):
            print("CAREFUL - More patients matched in output!")
            return 0
        if len(correct) > len(output):
            print("Less patients matched than correct.")
            return 0
        
        # For P1 - Just make sure all pairs are valid, and that each patient id is unique and valid.
        ids = collections.defaultdict(lambda: False)
        for id1, id2 in output:
            if ids[id1] or ids[id2] or id1 == id2:
                # Not unique patients
                return 0
            ids[id1] = True
            ids[id2] = True
            if (id1 not in self.analysis) or (id2 not in self.analysis):
                # Blank entry patients, or malformed.
                return 0
            p1 = self.analysis[id1]
            p2 = self.analysis[id2]
            if p1[1] != query or p2[1] != query:
                # Not the correct practitioner
                return 0
            if abs(p1[0] - p2[0]) >= 1:
                # Too far apart
                return 0

        # Lastly, just make sure the sums are the same (within 1e-6).
        correct_sum = 0
        output_sum = 0
        for (id1, id2), (id3, id4) in zip(correct, output):
            correct_sum += 1 - pow(self.analysis[id1][0] - self.analysis[id2][0], 2)
            output_sum += 1 - pow(self.analysis[id3][0] - self.analysis[id4][0], 2)
        if correct_sum - output_sum > 1e-6:
            # Correct sum is better by 1e-6.
            return 0
        if output_sum - correct_sum > 1e-6:
            # VERY BAD - Completely fine solution beats ours.
            raise ValueError("This is very bad, you need to analyse this solution.")
        return 1
