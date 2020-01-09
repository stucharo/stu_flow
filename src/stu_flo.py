import re

import pandas

regex = {
    "input_file": re.compile(r"INPUT\wFILE\s*\'\w*\'"),
    "author": re.compile(r"AUTHOR\s*\'\w*\'"),
    "branch": re.compile(r"BRANCH\s*\'\w*\'"),
}

class PPL:

    def __init__(self, path):
        self.path = path
        self.branches = []

    def parse(self):
        with open(self.path, 'r') as f:
            data = f.read()
        
        matches = {k: rx.findall(data) for k, rx in regex.items()}
        print(matches)

ppl = PPL('tests\\test_files\\FC1_rev01.ppl')
ppl.parse()

# print(ppl.author)