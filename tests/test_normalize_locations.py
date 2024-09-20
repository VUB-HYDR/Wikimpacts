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
            ("Kings, California", "United States", ["USA.5.16_1"]),
            ("Amman", "United States", []),
        ],
    )
    def test__get_american_area(self, area, country, expected):
        norm = refresh_fixture()
        assert norm._get_american_area(area, country) == expected
