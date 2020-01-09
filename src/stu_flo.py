import re
import sys

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
        self.branches = []

    def parse(self):
        with open(self.path, 'r') as f:
            data = f.read()
        
        matches = {k: rx.findall(data) for k, rx in regex.items()}
        self.build_object(matches)

    def build_object(self, matches):
        for k, v in matches.items():
            if k == "branch":
                getattr(self, f"process_{k}_list")(v)

    def process_branch_list(self, branch_list):
        for branch in branch_list:
            b = branch.split()
            name = str(b[1][1:-1])
            count = int(b[2])
            vals = np.array(b[3:], dtype=np.float)
            values = np.split(vals, len(vals) / (count+1))
            self.branches.append(Branch(name, count, values))

class Branch:

    def __init__(self, name, count, values):
        self.name = name
        self.count = count
        self.values = values



ppl = PPL('tests\\test_files\\FC1_rev01.ppl')
ppl.parse()
for b in ppl.branches:
    print(b.name, b.count, b.values)