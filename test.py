import re
import sys
import datetime
from dateutil import parser as parser
from dataclasses import dataclass, field
from typing import List
import datetime

import numpy as np
import pandas as pd
import h5py

re_num = r"[\+|-]?\d*\.*\d+(?:[e|E][\+|-]?\d+)?"

ppl_regex_strings = [
    r"\'(OLGA) ([\d+.]*\d)\'",
    r"(INPUT FILE)\n\'(.*)\'",
    r"(PVT FILE)\n\'(.*)\'",
    r"(RESTART FILE)\n\'(.*)\'",
    r"(DATE)\n\'(.*)\'",
    r"(PROJECT)\n\'(.*)\'",
    r"(TITLE)\n\'(.*)\'",
    r"(AUTHOR)\n\'(.*)\'",
    f"(NETWORK)\n({re_num})",
    r"(GEOMETRY)\s*\'\s*\((.*)\)\s*\'",
    rf"(BRANCH)\n\'(.*)\'\n(\d*)((?:\s*{re_num})*)",
    r"(CATALOG)\s*(\d*)((?:\n.+\s*\'(?:BOUNDARY|SECTION):\'\s*\'BRANCH:\'\s*\'.*\'\s*\'\(.*\)\'\s*\'.*\')*)",
    rf"(TIME SERIES)\s*\'\s*\((.*)\)\s*\'((?:\s*{re_num})*)",
]


def ppl_to_hdf5(ppl_file_path, hdf5_file_name):
    ppl_matches = parse_ppl_file(ppl_file_path)
    with h5py.File(f"{hdf5_file_name}.h5", "w") as hdf5:
        build_hdf5_from_regex_matches(hdf5, ppl_matches)


def parse_ppl_file(ppl_file_path):
    regex = re.compile("|".join(ppl_regex_strings))
    with open(ppl_file_path, "r") as f:
        data = f.read()
    matches = [tuple(v for v in m if v != "") for m in regex.findall(data)]
    return matches


keywords = [
    "olga",
    "input_file",
    "pvt_file",
    "restart_file",
    "date",
    "project",
    "title",
    "author",
    "network",
    "geometry",
]


def build_hdf5_from_regex_matches(hdf5_file, matches):
    for match in matches:
        keyword = match[0].lower().replace(" ", "_")
        if keyword in keywords:
            hdf5_file.attrs.create(keyword, match[1])
    branches = [match for match in matches if match[0].lower() == "branch"]
    catalog = [match for match in matches if match[0].lower() == "catalog"][0]
    time_series = [match for match in matches if match[0].lower() == "time series"][0]
    add_time_series_data_to_hdf5_file(hdf5_file, branches, catalog, time_series)


def add_time_series_data_to_hdf5_file(hdf5_file, branches, catalog, time_series):
    create_branches_in_hdf5_file(hdf5_file, branches)
    add_ts_as_dataframes(hdf5_file, catalog, time_series)


def create_branches_in_hdf5_file(hdf5_file, branches):
    for branch in branches:
        geometry = pd.DataFrame(
            np.reshape(branch[3].strip().split(), (2, int(branch[2]) + 1)).T.astype(
                np.float64
            ),
            columns=["Length", "Elevation"],
        )
        hdf5_file.create_group(branch[1])
        hdf5_file[f"/{branch[1]}"].attrs.create("geometry", geometry)


def add_ts_as_dataframes(hdf5_file, catalog, time_series):
    catalog, time_steps = build_catalog_with_ts(catalog, time_series)
    hdf5_file.attrs.create("time_steps", np.array(time_steps))
    add_ts_to_branches(hdf5_file, catalog)

def build_catalog_with_ts(catalog, time_series):
    cat = build_catalog(catalog)
    cat_inc = len(cat) + 1
    time_steps = []
    for n, v in enumerate(time_series[2].strip().split("\n")):
        row = n % cat_inc
        if row == 0:
            time_steps.append(float(v))
        else:
            cat[row - 1]['time_series'].append(np.array(v.split(), dtype=np.float))
    return cat, time_steps

def build_catalog(catalog):
    p = re.compile(
        r"(.*) \'(SECTION|BOUNDARY):\' \'BRANCH:\' \'(.*)\' \'\((.*)\)\' \'(.*)\'"
    )
    cat = []
    cat_list = catalog[2].strip().split("\n")
    for c in cat_list:
        m = p.findall(c)[0]
        cat.append({"symbol": m[0], "kind": m[1], "branch": m[2], "units": m[3], "description": m[4], "time_series": []})
    return cat

def add_ts_to_branches(hdf5_file, catalog):
    for branch in hdf5_file.keys():
        print(hdf5_file[f"/{branch}"].attrs.get("geometry"))



def _generate_branch_data(self):
    for c in self.catalog:
        self.branches[c.branch].catalogs.append(c)

    times = len(self.time_series)
    for _, branch in self.branches.items():
        nodes = branch.geometry.shape[0]
        sections = len([c for c in branch.catalogs if c.kind == "SECTION"])
        s = np.zeros((nodes - 1, times, sections))
        b = np.zeros((nodes, times, len(branch.catalogs) - sections))
        i_bound = i_sec = 0
        for cat in branch.catalogs:
            if cat.kind == "SECTION":
                s[:, :, i_sec] = np.array(cat.time_series).T
                i_sec += 1
            else:
                b[:, :, i_bound] = np.array(cat.time_series).T
                i_bound += 1

        b = b.reshape((np.prod(b.shape[:-1]), b.shape[-1]))
        midx_b = pd.MultiIndex.from_product(
            [branch.geometry["Length"], self.time_series]
        )
        branch.boundaries = pd.DataFrame(
            data=b,
            index=midx_b,
            columns=[c.symbol for c in branch.catalogs if c.kind == "BOUNDARY"],
        )

        s = s.reshape((np.prod(s.shape[:-1]), s.shape[-1]))
        midx_s = pd.MultiIndex.from_product(
            [branch.geometry["Length"][:-1], self.time_series]
        )
        branch.sections = pd.DataFrame(
            data=s,
            index=midx_s,
            columns=[c.symbol for c in branch.catalogs if c.kind == "SECTION"],
        )


ppl_to_hdf5("tests\\test_files\\SD1H_35.ppl", "test")
hdf = h5py.File("test.h5", "r")
print(hdf.keys())
hdf.close()


"""


class PPLReader:
    pass

    regex_strings = [
        r"\'(OLGA) ([\d+.]*\d)\'",
        r"(INPUT FILE)\n\'(.*)\'",
        r"(PVT FILE)\n\'(.*)\'",
        r"(RESTART FILE)\n\'(.*)\'",
        r"(DATE)\n\'(.*)\'",
        r"(PROJECT)\n\'(.*)\'",
        r"(TITLE)\n\'(.*)\'",
        r"(AUTHOR)\n\'(.*)\'",
        f"(NETWORK)\n({re_num})",
        r"(GEOMETRY)\s*\'\s*\((.*)\)\s*\'",
        rf"(BRANCH)\n\'(.*)\'\n(\d*)((?:\s*{re_num})*)",
        r"(CATALOG)\s*(\d*)((?:\n.+\s*\'(?:BOUNDARY|SECTION):\'\s*\'BRANCH:\'\s*\'.*\'\s*\'\(.*\)\'\s*\'.*\')*)",
        rf"(TIME SERIES)\s*\'\s*\((.*)\)\s*\'((?:\s*{re_num})*)",
    ]

    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        regex = re.compile("|".join(self.regex_strings))
        with open(self.file_path, "r") as f:
            data = f.read()
        m = [tuple(v for v in m if v != "") for m in regex.findall(data)]
        ppl = PPL()
        ppl.build_from_regex_matches(m)
        return ppl


class PPL:

    processors = {
        "OLGA": "_process_olga_version",
        "INPUT FILE": "_process_standard_string",
        "PVT FILE": "_process_standard_string",
        "RESTART FILE": "_process_standard_string",
        "DATE": "_process_date",
        "PROJECT": "_process_standard_string",
        "TITLE": "_process_standard_string",
        "AUTHOR": "_process_standard_string",
        "NETWORK": "_process_network",
        "GEOMETRY": "_process_standard_string",
        "BRANCH": "_process_branch",
        "CATALOG": "_process_catalog",
        "TIME SERIES": "_process_time_series",
    }

    def __init__(self):
        self.olga = None
        self.input_file = None
        self.pvt_file = None
        self.restart_file = None
        self.date = None
        self.project = None
        self.title = None
        self.author = None
        self.network = None
        self.geometry = None
        self.branches = {}
        self.catalog = []
        self.time_series = []

    def build_from_regex_matches(self, matches):
        for match in matches:
            f = getattr(self, self.processors[match[0].upper()])
            f(match)
        self._generate_branch_data()

    def build_from_regex_matches(self, matches):
        for match in matches:
            f = getattr(self, self.processors[match[0].upper()])
            f(match)
        self._generate_branch_data()

    def _process_standard_string(self, match):
        attr = match[0].lower().replace(" ", "_")
        setattr(self, attr, match[1])

    def _process_olga_version(self, match):
        self.olga_version = match[1]

    def _process_date(self, match):
        self.date = parser.parse(match[1], yearfirst=True)

    def _process_network(self, match):
        self.network = int(match[1])

    def _process_branch(self, match):
        name = match[1]
        count = int(match[2])
        geometry = pd.DataFrame(
            np.reshape(match[3].split(), (2, count + 1)).T.astype(np.float64),
            columns=["Length", "Elevation"],
        )
        self.branches[name] = Branch(name, count, geometry)

    def _process_catalog(self, match):
        p = re.compile(
            r"(.*) \'(SECTION|BOUNDARY):\' \'BRANCH:\' \'(.*)\' \'\((.*)\)\' \'(.*)\'"
        )
        cat_list = match[2].strip().split("\n")
        for cat in cat_list:
            m = p.findall(cat)[0]
            self.catalog.append(Catalog(m[0], m[1], m[2], m[3], m[4]))
        if len(self.catalog) != int(match[1]):
            raise Exception

    def _process_time_series(self, match):
        # convert time series data to a list of floats for time value and Pandas Series' for time series data
        time_series = [
            np.array(r.split(), dtype=np.float)
            if n % (len(self.catalog) + 1) > 0
            else float(r)
            for n, r in enumerate(match[2].strip().split("\n"))
        ]
        for n, v in enumerate(time_series):
            row = n % (len(self.catalog) + 1)
            if row == 0:
                self.time_series.append(v)
            else:
                self.catalog[row - 1].time_series.append(v)

    def _generate_branch_data(self):
        for c in self.catalog:
            self.branches[c.branch].catalogs.append(c)

        times = len(self.time_series)
        for _, branch in self.branches.items():
            nodes = branch.geometry.shape[0]
            sections = len([c for c in branch.catalogs if c.kind == "SECTION"])
            s = np.zeros((nodes - 1, times, sections))
            b = np.zeros((nodes, times, len(branch.catalogs) - sections))
            i_bound = i_sec = 0
            for cat in branch.catalogs:
                if cat.kind == "SECTION":
                    s[:, :, i_sec] = np.array(cat.time_series).T
                    i_sec += 1
                else:
                    b[:, :, i_bound] = np.array(cat.time_series).T
                    i_bound += 1

            b = b.reshape((np.prod(b.shape[:-1]), b.shape[-1]))
            midx_b = pd.MultiIndex.from_product(
                [branch.geometry["Length"], self.time_series]
            )
            branch.boundaries = pd.DataFrame(
                data=b,
                index=midx_b,
                columns=[c.symbol for c in branch.catalogs if c.kind == "BOUNDARY"],
            )

            s = s.reshape((np.prod(s.shape[:-1]), s.shape[-1]))
            midx_s = pd.MultiIndex.from_product(
                [branch.geometry["Length"][:-1], self.time_series]
            )
            branch.sections = pd.DataFrame(
                data=s,
                index=midx_s,
                columns=[c.symbol for c in branch.catalogs if c.kind == "SECTION"],
            )

    def to_hdf5(self, filename):
        with h5py.File(f"{filename}.h5", 'w') as hdf5:
            hdf5.attrs.create("olga", str(self.olga))
            hdf5.attrs.create("input_file", self.input_file)
            hdf5.attrs.create("pvt_file", self.pvt_file)
            hdf5.attrs.create("restart_file", self.restart_file)
            hdf5.attrs.create("date", str(self.date))
            hdf5.attrs.create("project", self.project)
            hdf5.attrs.create("title", self.title)
            hdf5.attrs.create("author", self.author)


@dataclass
class Catalog:

    symbol: str
    kind: str
    branch: str
    units: str
    description: str
    time_series: List[np.ndarray] = field(default_factory=list)

    def __repr__(self):
        return self.symbol


@dataclass
class Branch:

    name: str
    count: int
    geometry: pd.DataFrame
    catalogs: List[Catalog] = field(default_factory=list)


ppl = PPLReader("tests\\test_files\\SD1H_35.ppl").read()
ppl.to_hdf5("test")
hdf = h5py.File("test.h5", 'r')
print(hdf.attrs["olga"])
hdf.close()
"""
