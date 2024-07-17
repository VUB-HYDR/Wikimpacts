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
                [0.39933993399339934, 0.9999179184109004],
            ),
            (
                (
                    {"Num_Mix": 0, "Num_Max": 10, "Start_Date_Year": 2030},
                    [
                        {"Num_Min": 2, "Num_Max": 91, "Start_Date_Year": 2030},
                        {"Num_Min": 0, "Num_Max": 10, "Start_Date_Year": 2031},
                    ],
                ),
                None,
            ),
        ],
    )
    def test_calc_similarity(self, test_input, expected):
        matcher = SpecificInstanceMatcher()
        if expected:
            assert matcher.calc_similarity(test_input[0], test_input[1]) == expected
        else:
            with pytest.raises(UnboundLocalError):
                matcher.calc_similarity(test_input[0], test_input[1])
