from pathlib import Path
from random import randint

import numpy as np

# import the open_PPL function to let you create a PPL data structure
from src.stu_flo import open_PPL

# open a PPL file using it's path
ppl_file_path = "tests\\test_files\\32in_Peak_Cond_1200MMscfd.ppl"
ppl = open_PPL(Path(ppl_file_path))

# poke around in the PPL object
print("Here's some metadata...")
print(f"    Author: {ppl.author}")
print(f"    Date: {ppl.date}")

print("\n\nHere's a list of branch names...")
for branch in ppl.branches:
    print(f"    {branch.name}")

# pick a random branch
random_branch_number = randint(0, len(ppl.branches) - 1)
branch = ppl.branches[random_branch_number]
print("\n\nHere's some info about a random branch...")
print(f"    Name: {branch.name}")
print(f"    Nummber of values in each set: {branch.count}")
for n, v in enumerate(branch.values):
    print(f"    Values for {branch.name} set {n+1}: {v}")

# explore the dataframe
d = ppl.data
# show the top 3 rows
print(f"\n\n{d.head(3)}")

# show all rows where 'symbol' == 'GLT' and 'branch' == 'old_offshore'
print(f"\n\n{d[(d['symbol']=='GLT') & (d['branch']=='old_offshore')]}")

# then filter out just the time series data and convert to a numpy array...
data = d[(d['symbol']=='GLT') & (d['branch']=='old_offshore')].data
print(f"\n\n{np.array(data)}")