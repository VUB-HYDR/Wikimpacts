import pytest

from Evaluation.matcher import SpecificInstanceMatcher


class TestSpecificInstanceMatcher:
    @pytest.mark.parametrize(
        "gold_instance, sys_list, expected",
        [
            (
                {"Num_Min": 0, "Num_Max": 10, "Start_Date_Year": 2030},
                [
                    {"Num_Min": 2, "Num_Max": 91, "Start_Date_Year": 2030},
                    {"Num_Min": 0, "Num_Max": 10, "Start_Date_Year": 2031},
                ],
                [0.39933993399339934, 0.9999179184109004],
            ),
            (
                {"Num_Mix": 0, "Num_Max": 10, "Start_Date_Year": 2030},
                [
                    {"Num_Min": 2, "Num_Max": 91, "Start_Date_Year": 2030},
                    {"Num_Min": 0, "Num_Max": 10, "Start_Date_Year": 2031},
                ],
                None,
            ),
        ],
    )
    def test_calc_similarity(self, gold_instance, sys_list, expected):
        matcher = SpecificInstanceMatcher()
        if expected:
            assert matcher.calc_similarity(gold_instance, sys_list) == expected
        else:
            with pytest.raises(UnboundLocalError):
                matcher.calc_similarity(gold_instance, sys_list)

    @pytest.mark.parametrize(
        "test_gold_list, test_sys_list, expected_gold, expected_sys",
        [
            (
                # gold_list
                [
                    {
                        "Num_Min": 2,
                        "Num_Max": 82,
                        "Start_Date_Year": 2030,
                        "Location_Norm": ["Amman", "Zarqa"],
                    },
                    {
                        "Num_Min": 2,
                        "Num_Max": 91,
                        "Start_Date_Year": 2030,
                        "Location_Norm": ["Uppsala", "Stockholm"],
                    },
                    {
                        "Num_Min": 0,
                        "Num_Max": 10,
                        "Start_Date_Year": 2031,
                        "Location_Norm": ["Paris", "Lyon"],
                    },
                ],
                # sys_list
                [
                    {
                        "Num_Min": 0,
                        "Num_Max": 11,
                        "Start_Date_Year": 2031,
                        "Location_Norm": ["Lyon"],
                    },
                    {
                        "Num_Min": 1,
                        "Num_Max": 84,
                        "Start_Date_Year": 2029,
                        "Location_Norm": ["Uppsala", "Zarqa"],
                    },
                    {
                        "Num_Min": 2,
                        "Num_Max": 91,
                        "Start_Date_Year": 2030,
                        "Location_Norm": ["Stockholm"],
                    },
                    {
                        "Num_Min": 7,
                        "Num_Max": 30,
                        "Start_Date_Year": 2030,
                        "Location_Norm": ["Uppsala", "Linköping"],
                    },
                ],
                # gold
                [
                    {
                        "Num_Min": 2,
                        "Num_Max": 82,
                        "Start_Date_Year": 2030,
                        "Location_Norm": ["Amman", "Zarqa"],
                    },
                    {
                        "Num_Min": 2,
                        "Num_Max": 91,
                        "Start_Date_Year": 2030,
                        "Location_Norm": ["Uppsala", "Stockholm"],
                    },
                    {
                        "Num_Min": 0,
                        "Num_Max": 10,
                        "Start_Date_Year": 2031,
                        "Location_Norm": ["Paris", "Lyon"],
                    },
                    {
                        "Num_Min": None,
                        "Num_Max": None,
                        "Start_Date_Year": None,
                        "Location_Norm": None,
                    },
                ],
                # sys
                [
                    {
                        "Num_Min": 1,
                        "Num_Max": 84,
                        "Start_Date_Year": 2029,
                        "Location_Norm": ["Uppsala", "Zarqa"],
                    },
                    {
                        "Num_Min": 2,
                        "Num_Max": 91,
                        "Start_Date_Year": 2030,
                        "Location_Norm": ["Stockholm"],
                    },
                    {
                        "Num_Min": 0,
                        "Num_Max": 11,
                        "Start_Date_Year": 2031,
                        "Location_Norm": ["Lyon"],
                    },
                    {
                        "Num_Min": 7,
                        "Num_Max": 30,
                        "Start_Date_Year": 2030,
                        "Location_Norm": ["Uppsala", "Linköping"],
                    },
                ],
            ),
            # corner case
            ([], [], [], []),
            (
                [{"Num_Min": 1}],
                [{"Num_Min": 1000}],
                [{"Num_Min": 1}, {"Num_Min": None}],
                [{"Num_Min": None}, {"Num_Min": 1000}],
            ),
        ],
    )
    def test_matcher(self, test_gold_list, test_sys_list, expected_gold, expected_sys):
        matcher = SpecificInstanceMatcher()

        assert matcher.match(gold_list=test_gold_list, sys_list=test_sys_list) == (
            expected_gold,
            expected_sys,
        )
