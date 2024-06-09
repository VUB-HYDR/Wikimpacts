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
            ("Losses between $11 million and $12 million", None),
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
        ],
    )
    def test__check_for_approximation(self, test_input, expected):
        nlp, norm = refresh_fixture()
        assert norm._check_for_approximation(
            nlp(test_input), labels=["CARDINAL", "MONEY", "QUANTITY"]
        ) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [("110-352", (110, 352)), ("110 - 352", (110, 352))],
    )
    def test__extract_range(self, test_input, expected):
        _, norm = refresh_fixture()
        assert norm._extract_range(test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            # ("23mil dollars", (23000000, 23000000, 0)), # fails!
            ("23mil", (23000000, 23000000, 0)), # fails!
            ("110 - 352", (110, 352, 0)),
            ("between 11 and 17 people were affected", (11, 17, 1)),
            ("Nearly 300 homes were destroyed", (300, 300, 1)),
            ("Nearly 300 homes were destroyed", (300, 300, 1)),
        ],
    )
    def test_extract_numbers(self, test_input, expected):
        _, norm = refresh_fixture()
        assert norm.extract_numbers(test_input) == expected
