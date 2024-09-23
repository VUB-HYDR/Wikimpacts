import os

import pytest

from Database.scr.normalize_locations import NormalizeLocation


def refresh_fixture():
    print("CWD", os.getcwd())
    norm = NormalizeLocation(
        gadm_path="Database/data/gadm_world.csv",
        unsd_path="Database/data/UNSD — Methodology.csv",
    )
    return norm


class TestNormalizeLocations:
    @pytest.mark.parametrize(
        "area, country, expected",
        [
            ("Arizona", "United States", ["USA.3_1"]),
            ("United States", None, ["USA"]),
            ("United States", "United States", ["USA"]),
            ("Kings, California", "United States", ["USA.5.16_1"]),
            ("Amman", "United States", []),
            ("Kansas, United States", "United States", ["USA.17_1"]),
            ("Kansas", "United States", ["USA.17_1"]),
        ],
    )
    def test__get_american_area(self, area, country, expected):
        print("CWD", os.getcwd())
        norm = refresh_fixture()
        assert norm._get_american_area(area, country) == expected

    @pytest.mark.parametrize(
        "area, country, expected",
        [
            ("United States", None, ["USA"]),
            ("Kings, California", "United States", ["USA.5.16_1"]),
            ("Amman", "Jordan", ["JOR.2_1"]),
            ("Kansas, United States", "United States", ["USA.17_1"]),
            ("Kansas, United States", None, ["USA.17_1"]),
            ("Kansas", "United States", ["USA.17_1"]),
            ("Kansas", None, ["USA.17_1"]),
            ("Dijon", None, ["FRA.2.1.2_1"]),
            ("Amajyaruguru", None, ["RWA.1_1"]),
            ("Geumgwa", "South Korea", ["KOR.13.13.3_2"]),
            ("Geumgwa", None, ["KOR.13.13.3_2"]),
            ("Jerusalem", "Philippines", ["PHL.51.4.15_1"]),
            ("Geumsan", None, ["KOR.3.7_2"]),
            ("Al Dakhliyeh", "Oman", ["OMN.1_1"]),
            ("Penjab", None, ["PAK.7_1"]),
            ("Punjab", "India", ["IND.28_1"]),
            (None, "Pakistan", ["Z06", "PAK"]),
        ],
    )
    def test_get_gadm_gid(self, area, country, expected):
        norm = refresh_fixture()
        assert norm.get_gadm_gid(area, country) == expected
