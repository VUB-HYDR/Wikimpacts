import pytest

from Evaluation.matcher import SpecificInstanceMatcher


class TestSpecificInstanceMatcher:
    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (
                (
                    {"Num_Min": 0, "Num_Max": 10, "Start_Date_Year": 2030},
                    [
                        {"Num_Min": 2, "Num_Max": 91, "Start_Date_Year": 2030},
                        {"Num_Min": 0, "Num_Max": 10, "Start_Date_Year": 2031},
                    ],
                ),
                [0.3333333333333333, 0.6666666666666666],
            ),
        ],
    )
    def test_calc_similarity(self, test_input, expected):
        matcher = SpecificInstanceMatcher()
        assert matcher.calc_similarity(test_input[0], test_input[1]) == expected
