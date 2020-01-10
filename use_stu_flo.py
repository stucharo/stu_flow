from pathlib import Path
from random import randint

import numpy as np

# import the open_PPL function to let you create a PPL data structure
from src.stu_flo import open_PPL

# open a PPL file using it's path
ppl_file_path = "tests\\test_files\\AP_Lean_Fluid_Slugtracking_35MMscfd_60bara.ppl"
ppl = open_PPL(Path(ppl_file_path))
print('Opened PPL file.\n\n')

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

# pick a random symbol and branch to interrogate
sym = d.sample()["symbol"].values[0]
bch = d.sample()["branch"].values[0]

# show all rows where 'symbol' == 'GLT' and 'branch' == 'old_offshore'
print(f"\n\nShow all rows where 'symbol' == '{sym}' and 'branch' == '{bch}'...")
print(f"\n{d[(d['symbol']==sym) & (d['branch']==bch)]}")

# then filter out just the time series data and convert to a numpy array...
print("\n\nThen just the time series data...")
data = d[(d["symbol"] == sym) & (d["branch"] == bch)].data
print(f"\n{np.array(data)}")
