from pathlib import Path
from random import randint

# import the open_PPL function to let you create a PPL data structure
from src.stu_flo import open_PPL

# open a PPL file using it's path
ppl_file_path = "tests\\test_files\\FC1_rev01.ppl"
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

# explore the catalog
random_catalog_number = randint(0, len(ppl.catalog) - 1)
catalog = ppl.catalog[random_catalog_number]
print(f"\n\nHere is item {random_catalog_number+1} in the catalog...")
print(f"    Symbol: {catalog.symbol}")
print(f"    Kind: {catalog.kind}")
print(f"    Branch: {catalog.branch}")
print(f"    Units: {catalog.units}")
print(f"    Description: {catalog.description}")
