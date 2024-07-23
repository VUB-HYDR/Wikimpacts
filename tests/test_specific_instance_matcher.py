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
                        "Event_ID": "aA3",
                        "Num_Min": 2,
                        "Num_Max": 82,
                        "Start_Date_Year": 2030,
                        "Location_Norm": ["Amman", "Zarqa"],
                    },
                    {
                        "Event_ID": "aA3",
                        "Num_Min": None,
                        "Num_Max": 91,
                        "Start_Date_Year": 2030,
                        "Location_Norm": ["Uppsala", "Stockholm"],
                    },
                    {
                        "Event_ID": "aA3",
                        "Num_Min": 0,
                        "Num_Max": 10,
                        "Start_Date_Year": 2031,
                        "Location_Norm": ["Paris", "Lyon"],
                    },
                ],
                # sys_list
                [
                    {
                        "Event_ID": "aA3",
                        "Num_Min": 0,
                        "Num_Max": 11,
                        "Start_Date_Year": 2031,
                        "Location_Norm": ["Lyon"],
                    },
                    {
                        "Event_ID": "aA3",
                        "Num_Min": 1,
                        "Num_Max": 84,
                        "Start_Date_Year": 2029,
                        "Location_Norm": ["Uppsala", "Zarqa"],
                    },
                    {
                        "Event_ID": "aA3",
                        "Num_Min": 2,
                        "Num_Max": 91,
                        "Start_Date_Year": 2030,
                        "Location_Norm": ["Stockholm"],
                    },
                    {
                        "Event_ID": "aA3",
                        "Num_Min": 7,
                        "Num_Max": 30,
                        "Start_Date_Year": 2030,
                        "Location_Norm": ["Uppsala", "Linköping"],
                    },
                ],
                # gold
                [
                    {
                        "Event_ID": "aA3-0",
                        "Num_Min": 2,
                        "Num_Max": 82,
                        "Start_Date_Year": 2030,
                        "Location_Norm": ["Amman", "Zarqa"],
                    },
                    {
                        "Event_ID": "aA3-1",
                        "Num_Min": None,
                        "Num_Max": 91,
                        "Start_Date_Year": 2030,
                        "Location_Norm": ["Uppsala", "Stockholm"],
                    },
                    {
                        "Event_ID": "aA3-2",
                        "Num_Min": 0,
                        "Num_Max": 10,
                        "Start_Date_Year": 2031,
                        "Location_Norm": ["Paris", "Lyon"],
                    },
                    {
                        "Event_ID": "aA3-3",
                        "Num_Min": None,
                        "Num_Max": None,
                        "Start_Date_Year": None,
                        "Location_Norm": None,
                    },
                ],
                # sys
                [
                    {
                        "Event_ID": "aA3-0",
                        "Num_Min": 1,
                        "Num_Max": 84,
                        "Start_Date_Year": 2029,
                        "Location_Norm": ["Uppsala", "Zarqa"],
                    },
                    {
                        "Event_ID": "aA3-1",
                        "Num_Min": 2,
                        "Num_Max": 91,
                        "Start_Date_Year": 2030,
                        "Location_Norm": ["Stockholm"],
                    },
                    {
                        "Event_ID": "aA3-2",
                        "Num_Min": 0,
                        "Num_Max": 11,
                        "Start_Date_Year": 2031,
                        "Location_Norm": ["Lyon"],
                    },
                    {
                        "Event_ID": "aA3-3",
                        "Num_Min": 7,
                        "Num_Max": 30,
                        "Start_Date_Year": 2030,
                        "Location_Norm": ["Uppsala", "Linköping"],
                    },
                ],
            ),
            (
                [{"Event_ID": "aA3", "Num_Min": 1}],
                [{"Event_ID": "aA3", "Num_Min": 1000}],
                [
                    {"Event_ID": "aA3-0", "Num_Min": 1},
                    {"Event_ID": "aA3-1", "Num_Min": None},
                ],
                [
                    {"Event_ID": "aA3-0", "Num_Min": None},
                    {"Event_ID": "aA3-1", "Num_Min": 1000},
                ],
            ),
            # empty lists as input
            ([], [], [], []),
            # inconsistent schema
            (
                [
                    {
                        "Event_ID": "aA3",
                        "Num_Min": 0,
                        "Num_Max": 10,
                        "Start_Date_Year": 2030,
                    }
                ],
                [
                    {
                        "Event_ID": "aA3-0",
                        "Num_Mix": 2,
                        "Num_Max": 91,
                        "Start_Date_Year": 2030,
                    },
                    {
                        "Event_ID": "aA3-1",
                        "Num_Min": 0,
                        "Num_Max": 10,
                        "Start_Date_Year": 2031,
                    },
                ],
                None,
                None,
            ),
        ],
    )
    def test_matcher(self, test_gold_list, test_sys_list, expected_gold, expected_sys):
        matcher = SpecificInstanceMatcher(threshold=0.6, null_penalty=0.5)
        if expected_gold and expected_sys:
            assert matcher.match(gold_list=test_gold_list, sys_list=test_sys_list) == (
                expected_gold,
                expected_sys,
            )
        else:
            with pytest.raises(BaseException):
                matcher.match(test_gold_list, test_sys_list)
