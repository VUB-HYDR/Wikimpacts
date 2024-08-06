import pytest

from Database.scr.normalize_numbers import NormalizeNumber
from Database.scr.normalize_utils import NormalizeUtils


def refresh_fixture():
    utils = NormalizeUtils()
    nlp = utils.load_spacy_model("en_core_web_trf")
    norm = NormalizeNumber(nlp, locale_config="en_US.UTF-8")
    return nlp, norm


class TestNormalizeNumbers:
    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ("EUR19", "19"),
            ("$355 billion", "355 billion"),
            ("£23M", "23 million"),
            ("20k", "20 thousand"),
            (
                "Nearly 300 victims were discovered dead",
                "Nearly 300 victims were discovered dead",
            ),
            ("Almost $3B in losses", "Almost 3 billion in losses"),
        ],
    )
    def test__preprocess(self, test_input, expected):
        _, norm = refresh_fixture()
        assert norm._preprocess(test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ("19", [19]),
            ("$ 355 million", [355000000]),
            ("5 million", [5000000]),
            ("100 million", [100000000]),
            ("13 injuries", [13]),
            ("£ 23 billion", [23000000000]),
            ("23 were killed", [23]),
            ("100 thousand", [100000]),
            ("one hundred", [100]),
            ("none reported", [0]),
            ("no casualties were reported", [0]),
            ("unknown!", [None]),
            # cases meant to fail
            ("23 were injured and 11 are missing", None),
        ],
    )
    def test__extract_single_number(self, test_input, expected):
        _, norm = refresh_fixture()
        if isinstance(expected, list) and len(expected) == 1:
            assert norm._extract_single_number(test_input) == expected
        else:
            with pytest.raises(BaseException):
                norm._extract_single_number(test_input)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ("23 were injured and 11 are missing", [23, 11]),
            ("115 are still missing", [115]),
            # cases meant to fail
            ("Losses between $11 million and $12 million", None),
            ("Losses between 11 million and 12 million", None),  # todo: investigate
        ],
    )
    def test__extract_numbers_from_tokens(self, test_input, expected):
        nlp, norm = refresh_fixture()

        if isinstance(expected, list):
            assert norm._extract_numbers_from_tokens(nlp(test_input)) == expected
        else:
            with pytest.raises(BaseException):
                norm._extract_numbers_from_tokens(nlp(test_input))

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ("23 were injured and 11 are missing", [23, 11]),
            ("115 are still missing", [115]),
            # cases meant to fail
            # ("Losses between $11 million and $12 million", [11000000, 12000000]),
            # ("Losses between 11 million and 12 million",  [11000000, 12000000]), # todo: investigate
        ],
    )
    def test__extract_numbers_from_entities(self, test_input, expected):
        nlp, norm = refresh_fixture()

        if isinstance(expected, list):
            assert (
                norm._extract_numbers_from_entities(nlp(test_input), labels=["CARDINAL", "MONEY", "QUANTITY"])
                == expected
            )
        else:
            with pytest.raises(BaseException):
                norm._extract_numbers_from_entities(nlp(test_input), labels=["CARDINAL", "MONEY", "QUANTITY"])

    @pytest.mark.parametrize(
        "test_input, expected",
        [(">=12", "12"), ("one hundred and ten", "one hundred ten")],
    )
    def test__normalize_num(self, test_input, expected):
        nlp, norm = refresh_fixture()
        assert norm._normalize_num(nlp(test_input)) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [(">=12", "twelve"), ("200 million", "two hundred million")],
    )
    def test__normalize_num_to_words(self, test_input, expected):
        nlp, norm = refresh_fixture()
        assert norm._normalize_num(nlp(test_input), to_word=True) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (">=12", 1),
            ("200 million", 0),
            ("exactly 200", 0),
            ("more than 200", 1),
            ("2,000", 0),
            ("Greater than 700", 1),
        ],
    )
    def test__check_for_approximation(self, test_input, expected):
        nlp, norm = refresh_fixture()
        assert norm._check_for_approximation(nlp(test_input), labels=["CARDINAL", "MONEY", "QUANTITY"]) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ("110-352", (110, 352)),
            ("0 - 352", (0, 352)),
            ("23- 55", (23, 55)),
            ("24,501-61,672", (24501, 61672)),
            # not meant to handle this case
            (">=12", None),
            ("12", None),
            ("twelve and one hundred", None),
        ],
    )
    def test__extract_simple_range(self, test_input, expected):
        _, norm = refresh_fixture()
        assert norm._extract_simple_range(test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            # ("23mil dollars", (23000000, 23000000, 0)), # fails!
            ("23mil", (23000000, 23000000, 0)),
            ("110 - 352", (110, 352, 1)),
            ("between 11 and 17 people were affected", (11, 17, 1)),
            ("Nearly 300 homes were destroyed", (285, 315, 1)),
            ("$3.6 million", (3600000, 3600000, 0)),
            ("$35.63 million", (35630000, 35630000, 0)),
            ("$3.6 million", (3600000, 3600000, 0)),
            ("Damage: At least $129 million", (129000000, 199999999, 1)),
            ("At least 73", (73, 79, 1)),
            ("925000000", (925000000, 925000000, 0)),
            (925000000, (925000000, 925000000, 0)),
            (23.4, (23.4, 23.4, 0)),
            ("More than 7010 were killed", (7011, 7999, 1)),
            ("Less than 400", (301, 399, 1)),
            (
                "a minimum of 410 billion",
                (410000000000, 499999999999, 1),
            ),
            ("603+", (603, 699, 1)),
            (">=293", (293, 299, 1)),
            ("~293", (278, 307, 1)),
            (">= $27 million", (27000000, 29999999, 1)),
            ("$27 million or more", (27000000, 29999999, 1)),
            ("about A$500 million", (475000000, 525000000, 1)),
            ("over US$500 million", (500000001, 599999999, 1)),
            ("over USD 1.0 billion", (1000000001, 1999999999, 1)),
            ("15 billion yuan", (15000000000, 15000000000, 0)),
            ("100 million pesos", (100000000, 100000000, 0)),
        ],
    )
    def test_extract_numbers(self, test_input, expected):
        _, norm = refresh_fixture()
        assert norm.extract_numbers(test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ("there were tens of victims after the tornadoe", (20, 90)),
            (
                "Millions of kronoers were paid in damages",
                (2000000, 9000000),
            ),
            ("a few billion dollars", (2000000000, 6000000000)),
            ("a couple of hundreds", (200, 300)),
            ("there were several reported injuries", (2, 6)),
            ("there were several thousand reported injuries", (2000, 6000)),
            ("a dozen deaths were reported", (12, 12)),
            ("dozens of hundreds of homes were completely destroyed", (2 * 12 * 100, 6 * 12 * 100)),
            ("many were killed!", (20, 60)),
            ("Only a number of victims were found", (2, 6)),
            ("several millions of euros were wasted on this", (2000000, 9000000)),
            ("a large group of households was affected", (10 * 20 * 3, 10 * 60 * 5)),
            ("only one family was displaced", (1 * 3, 1 * 5)),
        ],
    )
    def test__extract_approximate_quantifiers(self, test_input, expected):
        _, norm = refresh_fixture()
        assert norm._extract_approximate_quantifiers(test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            # approx
            ("Almost 30", (28, 31)),  # rounded down! (floor(30*0.95), floor(30*1.05))
            ("approximately 7000000000 dollars", (6650000000, 7350000000)),
            ("Around 7000 homes were destroyed", (6650, 7350)),
            ("roughly, 4 injuries had been reported", (3, 4)),  # rounded down! (floor(4*0.95), floor(4*1.05))
            ("~45", (42, 47)),
            # over
            ("Greater than 300", (301, 399)),
            ("The number of deaths certainly exceeded 66", (67, 69)),
            ("more than 6 families were displaced", ((6 + 1) * 3, 6 * 5)),
            ("at least 3600 were reported missing", (3600, 3999)),
            ("no less than 55 injuries were reported in the media", (55, 59)),
            ("> 45", (46, 49)),
            (">=5", (5, 10)),  # created range by adding 5 since scale == 1
            ("greater than or equal to 9", (9, 14)),  # created range by adding 5 since scale == 1
            ("45+ deaths were reported by the news", (45, 49)),
            ("311,000,000+ Euros", (311000000, 399999999)),
            (">693 million", (693000001, 699999999)),
            # under
            ("less than 230000000 dollars were paid out in insurance costs", (200000001, 229999999)),
            ("No more than 23 million dollars", (20000001, 23000000)),
            ("Up to 7 billion dollars", (6000000001, 7000000000)),
            ("at most 3284 casualties were reported", (3001, 3284)),
            ("Up to 7000000 dollars", (6000001, 7000000)),
            ("Up to 7,000,000 dollars", (6000001, 7000000)),
            ("less than 1", (0, 0)),
            ("no more than 1 was injured", (0, 1)),
            ("≤7000000", (6000001, 7000000)),
            # cases this function does not handle; meant to raise BaseException
            ("six families were displaced", None),
        ],
    )
    def test__extract_complex_range(self, test_input, expected):
        _, norm = refresh_fixture()
        assert norm._extract_complex_range(test_input) == expected
