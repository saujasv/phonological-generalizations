import json
import argparse
import random
from glob import glob
from pathlib import Path

class Problem:
    def __init__(self, languages, families, problem_type, columns, data, ipa=False,
                 test_set=False, notes=None, features=None):
        self.languages = languages
        self.families = families
        self.type = problem_type
        self.ipa = ipa
        self.columns = columns
        self.data = data
        self.notes = notes
        self.test_set = test_set
        self.features = features
    
    def get_words(self):
        return [[''.join(self.data[i][j].split(' ')) if self.data[i][j].strip() != '?' else '' for j in range(len(self.data[0]))] for i in range(len(self.data))]

    def __repr__(self):
        '''representation'''
        return str(self)

    def __str__(self):
        '''string representation'''
        s = '=' * 64 
        s += '\n' + '<{} Problem in {}>'.format(self.type.capitalize(), str(self.languages))
        s += '\n\t' + 'language families: {}'.format(self.families)
        s += '\n\t' + 'task format: {}'.format(self.columns)
        s += '\n\t' + 'amount of data: {}'.format(len(self.data))
        s += '\n' + '=' * 64
        return s
    
    @classmethod
    def from_JSON(self, path):
        with open(path, 'r') as f:
            obj_dict = json.load(f)

        return Problem(
            obj_dict['languages'],
            obj_dict['families'],
            obj_dict['type'],
            obj_dict['columns'],
            obj_dict['data'],
            obj_dict['ipa'],
            obj_dict['test_set'],
            obj_dict['notes'],
            features=obj_dict['features'] if 'features' in obj_dict else None
        )
    
    def write_to_JSON(self, path):
        with open(path, 'w') as f:
            f.write(ProblemEncoder(ensure_ascii=False, indent=4).encode(self))

class ProblemEncoder(json.JSONEncoder):
    def __init__(self, **kwargs):
        super(ProblemEncoder, self).__init__(**kwargs)

    def default(self, o):
        return dict(o.__dict__)
