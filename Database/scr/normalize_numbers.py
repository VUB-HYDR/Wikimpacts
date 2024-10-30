from math import isnan
from typing import Dict, List, Tuple, Union

import regex
import spacy
from iso4217 import Currency
from num2words import num2words
from text_to_num import alpha2digit, text2num

from .log_utils import Logging


class NormalizeNumber:
    def __init__(self, nlp: spacy.language, locale_config: str):
        import locale

        locale.setlocale(locale.LC_ALL, locale_config)
        self.nlp = nlp
        self.atof = locale.atof
        self.lang = locale_config.split("_")[0]
        self.logger = Logging.get_logger("normalize_numbers")

        # synonym lists
        self.approximately = [
            "\~",
            "about",
            "almost",
            "around",
            "approach",
            "approached",
            "approaches",
            "approaching",
            "approx\.",
            "approximately",
            "approx",
            "as good as",
            "as many as",
            "as little as",
            "as much as",
            "as few as",
            "ballpark",
            "bordering on",
            "bordered on",
            "borders on",
            "give or take",
            "c\.",
            "ca\.",
            "cca",
            "circa",
            "close to",
            "closely",
            "in range",
            "in the direction of",
            "in the neighborhood of",
            "in the neighbourhood of",
            "in the range of",
            "in the vicinity of",
            "inexact",
            "inexactly",
            "just about",
            "more or less",
            "near to",
            "near about",
            "nearly",
            "not far from",
            "not quite",
            "on the edge of",
            "proximately",
            "practically",
            "roughly",
            "roundly",
            "speculated",
            "hypothized",
            "hypothised",
            "within",
            "within sight of",
            "within the range of",
            "virtually",
        ]

        self.family_synonyms = ["family", "families", "household"]

        self.over = [
            "\>",
            "above",
            "greater than",
            "more than",
            "over",
            "upwards of",
            "exceed",
            "exceeds",
            "exceeded",
            "exceeding",
        ]

        self.over_inclusive = [  # first
            "\+",
            "\>\=",
            "or more",
            "at least",
            "no less than",
            "not less than",
            "a minimum of",
            "a min of",
            "\≥",
            "greater than or equal to",
            "more than or equal to",
        ]

        self.under_inclusive = [
            "up to",
            "at most",
            "or less",
            "not more than",
            "a maximum of",
            "a max of",
            "no more than",
            "less than or equal to",
            "fewer than or equal to",
            "\≤",
            "\<\=",
        ]

        self.under = [
            "below",
            "downwards of",
            "fewer than",
            "under",
            "less than",
            "approaching",
            "approaches",
            "approched",
            "approach",
            "under",
            "\<",
        ]
        # TODO: implement this
        self.between = [
            "ranging between",
            # "from", reconsider
            # "to",
            "between",
            "spanning from",
        ]

        self.scales = [
            "hundred",
            "thousand",
            "million",
            "billion",
            "trillion",
        ]

        self.exactly = {
            "exactly",
            "precisely",
            "a total of",
            "only",
            # "no less than",
            "strictly",
        }

        self.zero_phrases = [
            "none",
            "no one",
            "no known",
            "zero",
            "no injuries",
            "no casualties",
            "no deaths",
            "no fatalities",
        ]
        self.unknown_phrases = [
            "minimal",
            "negligible",
            "inconsequential",
            "minor",
            "limited",
            "absent",
            "does not mention",
            "indefinite",
            "n/a",
            "na",
            "not available",
            "not certain",
            "not clear",
            "not defined",
            "not determined",
            "not identified",
            "not known",
            "not mentioned",
            "not determined",
            "not settled",
            "not specified",
            "uncertain",
            "unclear",
            "undefined",
            "undetermined",
            "unidentified",
            "unknown",
            "unpredicted",
            "unsettled",
            "unspecified",
        ]

    def _check_currency(self, currency_text: str) -> bool:
        try:
            Currency(currency_text)
            return True
        except ValueError:
            return False

    def _isfloat(self, text: str) -> bool:
        try:
            float(text)
            return True
        except ValueError:
            return False

    def _preprocess(self, text: str) -> str:
        lookup = {
            # case insensitive
            "style_1": {
                "k": "thousand",
                "m": "million",
                "b": "billion",
                "t": "trillion",
            },
            "style_2": {
                "mil": "million",
                "bil": "billion",
                "tril": "trillion",
            },
        }

        # remove currency
        text = " ".join(regex.sub(r"\p{Sc}|(~)|Rs\.|Rs", " \\g<1> ", text).split())

        # normalize shorthand style_1
        style_1_match_any = f"({'|'.join(lookup['style_1'].keys())}){{1}}"
        text = regex.sub(
            (r"(\d+){pattern}($|\s)".format(pattern=style_1_match_any)),
            lambda ele: f"{ele[1]} {lookup['style_1'][ele[2].lower()]} ",
            text,
            flags=regex.IGNORECASE,
        ).strip()

        # normalize shorthand style_2
        # otherwise, put spaces between words and digits
        text = regex.sub(
            r"\s+",
            " ",
            regex.sub(
                "[A-Za-z]+",
                lambda ele: (
                    f" {ele[0]} " if ele[0] not in lookup["style_2"].keys() else f' {lookup["style_2"][ele[0]]} '
                ),
                text,
            ),
        )

        # remove any iso-4217 currency codes
        text = regex.sub(
            "[A-Z]{3}\s+",
            lambda ele: ("" if self._check_currency(ele[0].strip()) == True else f" {ele[0]} "),
            text,
        ).strip()

        return text

    def _extract_single_number(self, text: str) -> List[float | None] | BaseException:
        number = None

        for z in self.zero_phrases:
            if z in text.lower().strip():
                return [0]

        for u in self.unknown_phrases:
            if u in text.lower().strip():
                return [None]
        try:
            # try extracting the number (in digits) directly (eg. "1,222")
            number = self.atof(text)
        except:
            try:
                # try extracting the number from words (eg. "two million")
                number = text2num(text, lang=self.lang, relaxed=True)
            except:
                # first process the case where a number followed by any exception scales
                if len(regex.findall(r"\b(?<!\.)\d+(?:,\d+)*(?:\.\d+)?\b", text)) == 1:
                    other_scales = ["crore", "lakh", "crores", "lakhs"]
                    matches = regex.findall(
                        r"\b(?<!\.)\d+(?:,\d+)*(?:\.\d+)?\b\s+(?:" + "|".join(other_scales) + ")",
                        text,
                    )
                    if len(matches):
                        numbers = [token.text for token in self.nlp(matches[0])]
                        try:
                            other_scales_2_num = {
                                "crore": 1e7,
                                "crores": 1e7,
                                "lakh": 1e5,
                                "lakhs": 1e5,
                            }
                            return [self.atof(numbers[0]) * other_scales_2_num[numbers[1]]]
                        except BaseException:
                            raise BaseException

                    else:
                        try:
                            # try normalizing the numbers to words, then extract the numbers
                            # (eg. "2 million" -> "two million" -> 2000000.0)
                            assert len(regex.findall(r"[0-9]+[,.]a?[0-9]*|[0-9]+", text)) == 1, BaseException
                            normalized_text = self._normalize_num(self.nlp(text), to_word=True)
                            number = text2num(normalized_text, lang=self.lang, relaxed=True)
                        except:
                            # handle decimals:
                            # if there is a decimal followed by a million/billion, etc
                            if len(regex.findall(r"[0-9]+[.]{1}[0-9]+", text)) == 1:
                                numbers = [token.text for token in self.nlp(text) if token.like_num]
                                if len(numbers) == 2 and len(set(numbers[1].split(" ")).intersection(self.scales)) != 0:
                                    try:
                                        return [
                                            self.atof(numbers[0]) * text2num(numbers[1], lang=self.lang, relaxed=True)
                                        ]
                                    except BaseException:
                                        raise BaseException
        try:
            assert number is not None
        except:
            raise BaseException()
        return [number]

    def _extract_numbers_from_tokens(self, doc: spacy.tokens.doc.Doc) -> List[float] | BaseException:
        numbers = []
        tmp_num = ""
        num_ranges = []
        try:
            for i, token in enumerate(doc):
                if token.tag_ == "CD":
                    try:
                        num = self._normalize_num(token.text, to_word=True)
                    except:
                        num = token.text
                    tmp_num += num
                    if token:
                        tmp_num += token.whitespace_
                if (i == len(doc) - 1 or token.tag_ != "CD") and tmp_num:
                    num_ranges.append(tmp_num.strip())
                    tmp_num = ""

            if num_ranges:
                for n in num_ranges:
                    try:
                        number = self.atof(n)
                    except:
                        number = text2num(n, lang=self.lang, relaxed=True)
                    numbers.append(number)

            return numbers
        except BaseException:
            raise BaseException

    @staticmethod
    def _normalize_num(doc, to_word=False) -> str:
        new = ""
        for token in doc:
            # some times wrong tags are assigned, so we need to check both the tags and if the token is a number by regex
            if (token.tag_ in ["CD", "SYM"] and token.text not in ["<", ">", "<=", ">=", "≥", "≤", "+"]) or (
                regex.match(r"\b(?<!\.)\d+(?:,\d+)*(?:\.\d+)?\b", token.text)
            ):
                try:
                    new += num2words(token.text) if to_word else token.text
                    if token.whitespace_:
                        new += token.whitespace_
                except:
                    new += token.text
                    if token.whitespace_:
                        new += token
        # remove "and"
        new = regex.sub(r"(and)[\s]", "", new)

        # remove leftover currency not detected by spaCy
        new = regex.sub(r"\p{Sc}", "", new)

        return new.strip()

    # deprecate! not in use?
    def _extract_numbers_from_entities(
        self, doc: spacy.tokens.doc.Doc, labels: List[str]
    ) -> List[float] | BaseException:
        numbers = []
        if not doc.ents:
            raise BaseException
        for ent in doc.ents:
            if ent.label_ in labels:
                # in case any numbers are spelled out, transcribe them
                new = ""
                if regex.match(r"[0-9]+\s[a-zA-Z]+", ent.text):
                    for i in ent.text.split(" "):
                        try:
                            new += num2words(i) + " "
                        except:
                            new += i + " "
                # if an entity is mixed, convert digits to words first
                transcribed_text = alpha2digit(
                    new if new else ent.text,
                    lang=self.lang,
                    ordinal_threshold=0,
                    relaxed=True,
                )
                if "MONEY" in labels and ent.label_ == "MONEY":
                    try:
                        return self._extract_numbers_from_tokens(doc)
                    except:
                        return self._extract_numbers_from_tokens(self.nlp(transcribed_text))

                try:
                    number = self.atof(transcribed_text)
                    numbers.append(number)
                except:
                    try:
                        normalized_num = self._normalize_num(self.nlp(transcribed_text), to_word=False)
                        numbers.append(self.atof(normalized_num))
                    except BaseException:
                        raise BaseException
        assert numbers != [], "No numbers extracted from entities"
        return numbers

    @staticmethod
    def _extract_spans(
        spans: List[Dict[str, Union[str, int]]],
    ):
        return [(span["start"], span["end"]) for span in spans]

    def _check_for_approximation(self, doc: spacy.tokens.doc.Doc, labels: List[str]) -> bool:
        tags = " ".join([token.tag_ for token in doc])
        ent_labels = [ent.label_ for ent in doc.ents]

        # or for combinations of a preposition, superlative, and number
        try:
            self.atof(doc.text)
            return 0
        except:
            # check for common keywords that suggest an approximation
            approx_phrases = []
            approx_phrases.extend(self.approximately)
            approx_phrases.extend(self.over)
            approx_phrases.extend(self.under)

            if any([k in doc.text.lower() for k in approx_phrases]):
                return 1

            if any([k in doc.text.lower() for k in self.exactly]):
                return 0

            # check for common POS tag combinations (example: "About 200 people" -> "RB CD NNS")
            # check for any math symbols (>=, ~, etc) or if a number ends with a plus/plus-minus sign
            if any([x in tags for x in ["NFP", "IN JJS CD", "RB CD NNS", "IN CD NNS", ":"]]) or regex.findall(
                r"[0-9]+(\+|±)|(=)*(>|<)(=)*|(~)", doc.text
            ):
                return 1

            # check if all tokens in the string are number/money-related
            elif all([token.like_num or token.tag_ == "$" for token in doc]):
                return 0

            # check the spans only if the text contains an adverb followed by a number
            # if ent spans are the same as num spans, it's not an approx
            elif "RB CD" == tags:
                ent_spans = self._extract_spans([ent for ent in doc.to_json()["ents"] if ent["label"] in labels])
                num_spans = self._extract_spans([token for token in doc.to_json()["tokens"] if token["tag"] in ["CD"]])
                return 0 if ent_spans and ent_spans == num_spans else 1

            # check if there are no entities in the specified labels
            elif not doc.ents or (len(set(ent_labels).intersection(labels)) != 0):
                return 0

            return 0

    def _extract_simple_range(self, text: str) -> Tuple[float, float] | None:
        sep = "-"
        for i in ("and", "to", "&"):
            if i in text:
                sep = i
                break
        try:
            nums = [x.replace(",", "") for x in text.split(sep)]
            if len(nums) == 2:
                try:
                    return (self.atof(nums[0].strip()), self.atof(nums[1].strip()))
                except:
                    return None
        except:
            # try again but first normalize the number first
            text = self._normalize_num(self.nlp(text), to_word=False)
            nums = text.split(sep)
            if len(nums) == 2:
                try:
                    return (self.atof(nums[0].strip()), self.atof(nums[1].strip()))
                except:
                    return None
        return None

    def _get_scale(self, n_init: float | int):
        """
        Determine the scale of a number
        """
        n = int(n_init) if isinstance(n_init, float) and n_init.is_integer() else n_init
        abs_n = abs(n)
        n_str = str(abs_n)
        scale = 0

        if isinstance(n, int):
            # Check if the last digit is zero
            trailing_zeros = len(n_str) - len(n_str.rstrip("0"))
            scale = 10**trailing_zeros

        elif isinstance(n, float):
            _, part_dec = n_str.split(".")
            scale = 10 ** (-len(part_dec))

        return n, scale

    def _extract_complex_range(self, text: str) -> Tuple[float, float] | None:
        phrases = {
            "approx": {"list": sorted(self.approximately, reverse=True)},
            "over_inclusive": {"list": sorted(self.over_inclusive, reverse=True)},
            "under_inclusive": {"list": sorted(self.under_inclusive, reverse=True)},
            "over": {"list": sorted(self.over, reverse=True)},
            "under": {"list": sorted(self.under, reverse=True)},
        }

        for k, v in phrases.items():
            any_digit = "[\d,.]*"
            expression = "({any_digit})\s*({scales})*\s*({phrases})[,.]*\s*({any_digit})\s*({scales})*"
            expression = expression.format(
                phrases="|".join(v["list"]),
                scales="|".join(self.scales),
                any_digit=any_digit,
            )
            matches = regex.findall(expression, text, flags=regex.IGNORECASE | regex.MULTILINE)

            for i in range(len(matches)):
                matches[i] = [x.strip().replace(",", "") for x in matches[i] if x != ""]
            matches = [x for x in matches if x]
            phrases[k]["matches"] = matches

        for k, v in phrases.items():
            if v["matches"]:
                if len(v["matches"]) == 1:
                    digits = [float(x) for x in v["matches"][0] if (x.isdigit() or self._isfloat(x))]
                    if any([x in self.scales for x in v["matches"][0]]):
                        try:
                            norm_text = [
                                x for x in v["matches"][0] if x in self.scales or (x.isdigit() or self._isfloat(x))
                            ]
                            num = self._extract_single_number(" ".join(norm_text))[0]
                        except BaseException as err:
                            self.logger.error(f"Could not infer number from {norm_text}. Error: {err}")
                            return None
                    else:
                        if len(digits) == 1:
                            num = digits[0]
                        else:
                            return None
                    lower_mod, upper_mod = (
                        (3, 5)
                        if any([x in [y.lower() for y in text.split()] for x in self.family_synonyms])
                        else (1, 1)
                    )
                    n, scale = self._get_scale(num)

                    if k == "approx":
                        return ((max(0, n - scale) * lower_mod), (n + scale) * upper_mod)
                    if "over" in k:
                        inc = 0 if "inclusive" in k else 1
                        return ((n + inc) * lower_mod, (n + scale + inc) * upper_mod)

                    if "under" in k:
                        inc = 0 if "inclusive" in k else 1
                        return (
                            max(0, n - scale - inc) * lower_mod,
                            max(0, n - inc) * upper_mod,
                        )
        return None

    def _extract_approximate_quantifiers(self, text: str) -> Tuple[float, float] | None:
        one, ten, hun, tho, mil, bil, tri = (
            1,
            10,
            100,
            1000,
            1000000,
            1000000000,
            1000000000000,
        )
        phrases = {
            "single": {
                "a single": one,
                "only one": one,
                "no more than one": one,
            },
            "scales": {
                "tens of": ten,
                "hundreds": hun,
                "thousands": tho,
                "tens of thousands": tho * ten,
                "hundreds of thousands": hun * tho,
                "millions": mil,
                "tens of millions": ten * mil,
                "hundreds of millions": hun * mil,
                "billions": bil,
                "tens of billions": ten * bil,
                "hundreds of billions": hun * bil,
                "trillions": tri,
                "tens of tillions": ten * tri,
                "hundreds of tillions": hun * tri,
            },
            "few": {
                "few dozen": one * 12,
                "group of": one,
                "number of": one,
                "few hundred": hun,
                "several hundred": hun,
                "few thousand": tho,
                "several thousand": tho,
                "few million": mil,
                "several million": mil,
                "few billion": bil,
                "several billion": bil,
            },
            "single_dozen": {
                "dozen hundred": hun * 12,
                "dozen thousand": tho * 12,
                "dozen million": mil * 12,
                "dozen billion": bil * 12,
            },
        }

        check_first = {
            "couple": {
                "couple of hundred": hun,
                "couple hundred": hun,
                "couple of thousand": tho,
                "couple thousand": tho,
                "couple of million": mil,
                "couple million": mil,
                "couple of billion": bil,
                "couple billion": bil,
            },
            "dozen": {
                "dozen hundred": hun * 12,
                "dozen thousand": tho * 12,
                "dozen million": mil * 12,
                "dozen billion": bil * 12,
                "dozens of hundred": hun * 12,
                "dozens of thousand": tho * 12,
                "dozens of million": mil * 12,
                "dozens of billion": bil * 12,
            },
            "many": {
                "large group of": ten,
            },
        }

        check_last = {
            "few": {
                "a few": one,
                "several": one,
            },
            "many": {
                "many": one,
            },
            "couple": {
                "a couple": one,
            },
            "single_dozen": {
                "a dozen": one * 12,
            },
        }

        ranges = {
            "scales": (2, 9),
            "single": (1, 1),
            "few": (2, 6),
            "couple": (2, 3),
            "dozen": (2, 6),
            "single_dozen": (1, 1),
            "many": (20, 60),
        }

        def _check(_dict, key, text):
            for phrase, degree in _dict[key].items():
                lower_range, upper_range = ranges[key]
                lower_mod, upper_mod = (3, 5) if any([x in text.lower() for x in self.family_synonyms]) else (1, 1)
                if phrase in text.lower():
                    return (
                        degree * lower_range * lower_mod,
                        degree * upper_range * upper_mod,
                    )

        for check_dict in (
            check_first,
            phrases,
            check_last,
        ):  # PLEASE MAINTAIN THE ORDER OF THESE LISTS!
            for k in check_dict.keys():
                output = _check(check_dict, k, text)
                if output:
                    return output
        return None

    def extract_numbers(
        self,
        text: Union[str, float, int],
        labels: List[str] = ["CARDINAL", "MONEY", "QUANTITY"],
    ) -> Tuple[Union[float, None], Union[float, None], Union[bool, None]]:
        if (isinstance(text, float) and not isnan(text)) or isinstance(text, int):
            return (text, text, 0)

        text = self._preprocess(text)
        doc = self.nlp(text.strip())
        approx = self._check_for_approximation(doc, labels)

        try:
            numbers = self._extract_simple_range(text)
            assert numbers, BaseException
            approx = 1
        except BaseException:
            try:
                numbers = self._extract_complex_range(text)
                assert numbers, BaseException
                approx = 1
            except BaseException:
                try:
                    cleaned_text = " ".join(regex.sub(r"\s+[A-Z]{1,3}\s+", " ", text).split())
                    numbers = self._extract_complex_range(cleaned_text)
                    assert numbers, BaseException
                    approx = 1
                except BaseException:
                    try:
                        numbers = self._extract_single_number(text)
                        assert numbers, BaseException
                    except:
                        cleaned_text = regex.sub(r"(\d+),(\d+)", r"\1\2", text)
                        cleaned_text = " ".join(
                            [x for x in cleaned_text.split() if (self._isfloat(x) or x.isdigit() or (x in self.scales))]
                        )
                        try:
                            numbers = self._extract_single_number(cleaned_text)
                            assert numbers, BaseException
                        except:
                            try:
                                numbers = self._extract_approximate_quantifiers(text)
                                assert numbers, BaseException
                                approx = 1
                            except BaseException:
                                try:
                                    # try extraction by spaCy NERs
                                    numbers = self.extract_numbers_from_entities(doc, labels)
                                    assert numbers, BaseException
                                except BaseException:
                                    try:
                                        # if no NERs were extacted or no NERs were useful, try extracting by token instead
                                        numbers = self._extract_numbers_from_tokens(doc)
                                        assert numbers, BaseException
                                        approx = 1 if len(numbers) == 2 else approx
                                    except BaseException:
                                        try:
                                            # if all fails, try by normalizing the numbers to words
                                            doc = self.nlp(self._normalize_num(doc), to_words=True)
                                            numbers = self.extract_numbers_from_entities(doc, labels)
                                        except BaseException:
                                            return (None, None, None)

        if numbers:
            numbers = sorted(numbers)
            if len(numbers) == 1:
                return (numbers[0], numbers[0], approx)
            elif len(numbers) == 2:
                return (numbers[0], numbers[1], approx)
        return (None, None, approx)
