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
        norm = refresh_fixture()
        assert norm._get_american_area(area, country) == expected
