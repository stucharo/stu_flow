import re
import sys
from dateutil import parser as parser
from dataclasses import dataclass, field
from typing import List
import itertools
import datetime

import numpy as np
import pandas as pd
import h5py

re_num = r"[\+|-]?\d*\.*\d+(?:[e|E][\+|-]?\d+)?"

regex = {
    "olga_version": re.compile(r"\'OLGA ([\d+.]*\d)\'"),
    "input_file": re.compile(r"INPUT FILE\n\'(.*)\'"),
    "restart_file": re.compile(r"RESTART FILE\n\'(.*)\'"),
    "date": re.compile(r"DATE\n\'(.*)\'"),
    "project": re.compile(r"PROJECT\n\'(.*)\'"),
    "title": re.compile(r"TITLE\n\'(.*)\'"),
    "author": re.compile(r"AUTHOR\n\'(.*)\'"),
    "network": re.compile(r"NETWORK\n(\d*)"),
    "branch": re.compile(
        f"BRANCH\n\'(.*)\'\n(\d*)((?:\s*{re_num})*)"
    ),
    "catalog": re.compile(
        r"CATALOG\s*(\d*)((?:\n.+\s*\'(?:BOUNDARY|SECTION):\'\s*\'BRANCH:\'\s*\'.*\'\s*\'\(.*\)\'\s*\'.*\')*)"
    ),
    "time_series": re.compile(
        r"TIME SERIES\s*\'\s*\(.*\)\s*\'(?:\s*-?\d+\.\d+e(?:\+|-)\d+)*"
    ),
}

def store_ppl_in_hdf5(ppl_path):
    ppl_data = _parse_ppl(ppl_path)
    _build_hdf5('test', ppl_data)
    return 'test'


def _parse_ppl(ppl_path):

    with open(ppl_path, "r") as f:
        data = f.read()

    matches = {
        k: v
        for k, v in {k: rx.findall(data) for k, rx in regex.items()}.items()
        if len(v) > 0
    }
    
    return matches

def _build_hdf5(hdf5_file, data):
    standard_strings = ["input_file", "restart_file", "project", "title", "author"]
    this_module = sys.modules[__name__]
    for k, v in data.items():
        if k in standard_strings:
            h5py.File(f"{hdf5_file}.h5", 'a')[k] = v[0]
        else:
            getattr(this_module, f"process_{k}_list")(hdf5_file, v)

def process_olga_version_list(hdf5_file, olga_version_list):
    h5py.File(f"{hdf5_file}.h5", 'a')['olga_version'] = olga_version_list[0]

def process_date_list(store, date_list):
    store['date'] = parser.parse(date_list[0], yearfirst=True)

def process_network_list(store, network_list):
    store['network'] = int(network_list[0])

def process_branch_list(self, branch_list):
    for branch in branch_list:
        name = branch[0]
        count = int(branch[1])
        vals = np.array(branch[2].split(), dtype=np.float)
        values = np.split(vals, len(vals) / (count + 1))
        self.branches.append(Branch(name, count, values))
    if len(self.branches) != self.network:
        raise Exception(
            f"Number of branches ({len(self.branches)}) does not equal value in PPL file ({self.network})."
        )

def process_catalog_list(self, catalog_list):
    catalog_length = int(catalog_list[0][0])
    catalog_item_re = re.compile(
        r"(.+) \s*\'(BOUNDARY|SECTION):\'\s*\'BRANCH:\'\s*\'(.*)\'\s*\'\((.*)\)\'\s*\'(.*)\'"
    )
    self.catalog = catalog_item_re.findall(catalog_list[0][1])
    if len(self.catalog) != catalog_length:
        raise Exception(
            f"Number of catalogue items ({len(self.catalog)}) does not equal value in PPL file ({int(catalog[1])})."
        )

def process_time_series_list(self, time_series_list):
    # convert time series data to a list of floats for time value and Pandas Series' for time series data
    time_series = [
        np.array(r.split(), dtype=np.float)
        if n % (len(self.catalog) + 1) > 0
        else float(r)
        for n, r in enumerate(time_series_list[0].split("\n")[1:])
    ]
    times = []
    series = []
    for n, v in enumerate(time_series):
        if n % (len(self.catalog) + 1) == 0:
            times.append(v)
        else:
            series.append(v)

    d = {
        "times": list(
            itertools.chain.from_iterable(
                itertools.repeat(x, len(self.catalog)) for x in times
            )
        ),
        "symbol": [str(c[0]) for c in self.catalog] * len(times),
        "kind": [c[1] for c in self.catalog] * len(times),
        "branch": [c[2] for c in self.catalog] * len(times),
        "units": [c[3] for c in self.catalog] * len(times),
        "description": [c[4] for c in self.catalog] * len(times),
        "data": series,
    }
    self.time_series = pd.DataFrame(data=d)



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
        self.catalog = []
        self.time_series = None

    def parse(self):
        with open(self.path, "r") as f:
            data = f.read()

        matches = {
            k: v
            for k, v in {k: rx.findall(data) for k, rx in regex.items()}.items()
            if len(v) > 0
        }
        #self.build_object(matches)

    def build_hdf5(self, matches):
        store = pd.HDFStore('test.h5')
        



    def build_object(self, matches):
        standard_strings = ["input_file", "restart_file", "project", "title", "author"]
        for k, v in matches.items():
            if k in standard_strings:
                setattr(self, k, v[0])
            else:
                getattr(self, f"process_{k}_list")(v)

    def process_olga_version_list(self, olga_version_list):
        self.olga_version = olga_version_list[0]

    def process_date_list(self, date_list):
        self.date = parser.parse(date_list[0], yearfirst=True)

    def process_network_list(self, network_list):
        self.network = int(network_list[0])

    def process_branch_list(self, branch_list):
        for branch in branch_list:
            name = branch[0]
            count = int(branch[1])
            vals = np.array(branch[2].split(), dtype=np.float)
            values = np.split(vals, len(vals) / (count + 1))
            self.branches.append(Branch(name, count, values))
        if len(self.branches) != self.network:
            raise Exception(
                f"Number of branches ({len(self.branches)}) does not equal value in PPL file ({self.network})."
            )

    def process_catalog_list(self, catalog_list):
        catalog_length = int(catalog_list[0][0])
        catalog_item_re = re.compile(
            r"(.+) \s*\'(BOUNDARY|SECTION):\'\s*\'BRANCH:\'\s*\'(.*)\'\s*\'\((.*)\)\'\s*\'(.*)\'"
        )
        self.catalog = catalog_item_re.findall(catalog_list[0][1])
        if len(self.catalog) != catalog_length:
            raise Exception(
                f"Number of catalogue items ({len(self.catalog)}) does not equal value in PPL file ({int(catalog[1])})."
            )

    def process_time_series_list(self, time_series_list):
        # convert time series data to a list of floats for time value and Pandas Series' for time series data
        time_series = [
            np.array(r.split(), dtype=np.float)
            if n % (len(self.catalog) + 1) > 0
            else float(r)
            for n, r in enumerate(time_series_list[0].split("\n")[1:])
        ]
        times = []
        series = []
        for n, v in enumerate(time_series):
            if n % (len(self.catalog) + 1) == 0:
                times.append(v)
            else:
                series.append(v)

        d = {
            "times": list(
                itertools.chain.from_iterable(
                    itertools.repeat(x, len(self.catalog)) for x in times
                )
            ),
            "symbol": [str(c[0]) for c in self.catalog] * len(times),
            "kind": [c[1] for c in self.catalog] * len(times),
            "branch": [c[2] for c in self.catalog] * len(times),
            "units": [c[3] for c in self.catalog] * len(times),
            "description": [c[4] for c in self.catalog] * len(times),
            "data": series,
        }
        self.time_series = pd.DataFrame(data=d)


@dataclass
class Branch:

    name: str
    count: int
    values: List[np.ndarray] = field(default_factory=list)


@dataclass
class Catalog:

    symbol: str
    kind: str
    branch: str
    units: str
    description: str
    data: np.ndarray


def open_PPL(path):
    ppl = PPL(path)
    ppl.parse()
    return ppl


if __name__ == "__main__":
    from pathlib import Path

    ppl_file_path = "tests\\test_files\\AP_Lean_Fluid_Slugtracking_35MMscfd_60bara.ppl"
    ppl = store_ppl_in_hdf5(ppl_file_path)
    print(ppl)
