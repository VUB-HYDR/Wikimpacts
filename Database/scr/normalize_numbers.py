from math import isnan
from typing import Dict, List, Tuple, Union

import regex
import spacy
from iso4217 import Currency
from num2words import num2words
from text_to_num import alpha2digit, text2num


class NormalizeNumber:
    def __init__(self, nlp: spacy.language, locale_config: str):
        import locale

        locale.setlocale(locale.LC_ALL, locale_config)
        self.nlp = nlp
        self.atof = locale.atof
        self.lang = locale_config.split("_")[0]

        # synonym lists
        self.approximately = [
            "about",
            "almost",
            "approaching",
            "approx",
            "approximately",
            "as good as",
            "ballpark",
            "between",
            "bordering on",
            "give or take",
            "c.",
            "ca.",
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
            "ranging between",
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

        self.over = [
            "a minimum of",
            "above",
            "approaching",
            "at least",
            "greater than",
            "more than",
            "over",
            "upwards of",
        ]

        self.under = [
            "a maximum of",
            "at most",
            "below",
            "downwards of",
            "fewer than",
            "less than",
            "under",
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
            "no more than",
            "no less than",
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
            "minimal",
            "no fatalities",
            "negligible",
            "inconsequential",
            "minor",
            "limited",
        ]
        self.unknown_phrases = [
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
            "unspecified"
            # "null", ##???
        ]

    def _check_currency(self, currency_text):
        try:
            Currency(currency_text)
            return True
        except ValueError:
            return False

    def _preprocess(self, text: str):
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

    def _extract_single_number(self, text: str) -> List[float] | BaseException:
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
            if (token.tag_ in ["CD", "SYM"] and token.text not in ["<", ">", "<=", ">="]) or (
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

    def _extract_range(self, text: str) -> Tuple[float]:
        try:
            nums = text.split("-")
            if len(nums) == 2:
                try:
                    return (self.atof(nums[0].strip()), self.atof(nums[1].strip()))
                except:
                    return None
        except:
            # try again but first normalize the number first
            text = self._normalize_num(self.nlp(text), to_word=False)
            nums = text.split("-")
            if len(nums) == 2:
                try:
                    return (self.atof(nums[0].strip()), self.atof(nums[1].strip()))
                except:
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
                "a few dozen": one * 12,
                "a group of": one,
                "a number of": one,
                "a few hundred": hun,
                "several hundred": hun,
                "a few thousand": tho,
                "several thousand": tho,
                "a few million": mil,
                "several million": mil,
                "a few billion": bil,
                "several billion": bil,
            },
            "single_dozen": {
                "a dozen hundred": hun * 12,
                "a dozen thousand": tho * 12,
                "a dozen million": mil * 12,
                "a dozen billion": bil * 12,
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
        }

        check_last = {
            "few": {
                # keep last!
                "a few": one,
                "several": one,
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
            "few": (2, 6),
            "couple": (2, 3),
            "dozen": (2, 6),
            "single_dozen": (1, 1),
        }

        def _check(_dict, key, text):
            for phrase, degree in _dict[key].items():
                lower_range, upper_range = ranges[key]
                if phrase in text.lower():
                    return (degree * lower_range, degree * upper_range)

        # check these first to avoid rule conflics
        for k in check_first.keys():
            output = _check(check_first, k, text)
            if output:
                return output

        for k in phrases.keys():
            output = _check(phrases, k, text)
            if output:
                return output

        # do a last sweep
        for k in check_last.keys():
            output = _check(check_last, k, text)
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
            # simplest approach, attempt to extract a single number
            numbers = self._extract_single_number(text)
        except BaseException:
            try:
                numbers = self._extract_range(text)
                assert numbers, BaseException
            except BaseException:
                try:
                    numbers = self._extract_approximate_quantifiers(text)
                    if numbers:
                        approx = 1
                    else:
                        raise BaseException
                except BaseException:
                    try:
                        # try extraction by spaCy NERs
                        numbers = self.extract_numbers_from_entities(doc, labels)
                    except BaseException:
                        try:
                            # if no NERs were extacted or no NERs were useful, try extracting by token instead
                            numbers = self._extract_numbers_from_tokens(doc)
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
