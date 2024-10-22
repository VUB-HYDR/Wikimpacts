import pytest

from Database.scr.normalize_locations import NormalizeLocation


def refresh_fixture():
    norm = NormalizeLocation(
        gadm_path="Database/data/gadm_world.csv",
        unsd_path="Database/data/UNSD — Methodology.csv",
    )
    return norm


class TestNormalizeLocations:
    @pytest.mark.parametrize(
        "area, expected",
        [
            ("Arizona, United States", ["USA.3_1"]),
            ("United States", ["USA"]),
            ("Kings, California, United States", ["USA.5.16_1"]),
            ("Amman, United States", None),
            ("Kansas, United States", ["USA.17_1"]),
            ("Kansas, United States", ["USA.17_1"]),
            ("Orange County, California, United States", ["USA.5.30_1"]),
            ("India", None),
        ],
    )
    def test__get_american_area(self, area, expected):
        norm = refresh_fixture()
        assert norm._get_american_area(area) == expected

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
            ("Orange County, California, United States", None, ["USA.5.30_1"]),
            (None, "Orange County, California, United States", ["USA.5.30_1"]),
            (None, "Netherlands", ["NLD"]),
            ("India", None, []),
            (None, "India", ["Z07", "IND", "Z01", "Z04", "Z05", "Z09"]),
        ],
    )
    def test_get_gadm_gid(self, area, country, expected):
        norm = refresh_fixture()
        assert norm.get_gadm_gid(area, country) == expected
