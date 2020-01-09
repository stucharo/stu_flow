import re
import sys
import datetime
from dataclasses import dataclass, field
from typing import List

import numpy as np

regex = {
    "olga_version": re.compile(r"\'OLGA [\d+.]*\d\'"),
    "input_file": re.compile(r"INPUT FILE\s*.*"),
    "restart_file": re.compile(r"RESTART FILE\s*.*"),
    "date": re.compile(r"DATE\s*.*"),
    "project": re.compile(r"PROJECT\s*.*"),
    "title": re.compile(r"TITLE\s*.*"),
    "author": re.compile(r"AUTHOR\s*.*"),
    "network": re.compile(r"NETWORK\s*.*"),
    "branch": re.compile(r"BRANCH\s*.*\s*[0-9]+[\s*-?\d*\.\d*]*"),
}

class PPL:

    def __init__(self, path):
        self.path = path
        self.initialise_variables()

    def initialise_variables(self):
        self.olga_version = None
        self.input_file = None
        self.restart_file = None
        self.date = None
        self.project = None
        self.title = None
        self.author = None
        self.network = None
        self.branches = []

    def parse(self):
        with open(self.path, 'r') as f:
            data = f.read()
        
        matches = {k: rx.findall(data) for k, rx in regex.items()}
        self.build_object(matches)

    def build_object(self, matches):
        standard_strings = [
            'input_file',
            'restart_file',
            'project',
            'title',
            'author',
        ]
        for k, v in matches.items():
            if k in standard_strings:
                setattr(self, k, v[0].split()[-1][1:-1])
            else:
                getattr(self, f"process_{k}_list")(v)

    def process_olga_version_list(self, olga_version_list):
        self.olga_version = olga_version_list[0].split()[-1][:-1]

    def process_date_list(self, date_list):
        date_str = date_list[0].split('\n')[-1][1:-1]
        self.date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

    def process_network_list(self, network_list):
        self.network = int(network_list[0].split()[-1])

    def process_branch_list(self, branch_list):
        for branch in branch_list:
            b = branch.split()
            name = str(b[1][1:-1])
            count = int(b[2])
            vals = np.array(b[3:], dtype=np.float)
            values = np.split(vals, len(vals) / (count+1))
            self.branches.append(Branch(name, count, values))

@dataclass
class Branch:

    name: str
    count: int
    values: List[np.ndarray] = field(default_factory=list)
    

def open_PPL(path):
    ppl = PPL(path)
    ppl.parse()
    return ppl

if __name__ == "__main__":

    ppl = open_PPL('tests\\test_files\\FC1_rev01.ppl')
    print(ppl.branches[0].values[0].shape)