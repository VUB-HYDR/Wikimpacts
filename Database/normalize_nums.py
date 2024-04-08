import regex
import spacy
from num2words import num2words
from text_to_num import alpha2digit, text2num
from typing import List


def load_spacy_model(spacy_model: str = "en_core_web_trf") -> spacy.language:
    try:
        nlp = spacy.load(spacy_model, enable=["transformer", "ner", "tagger"])
        print(f"SpaCy model '{spacy_model}' has been loaded")
    except OSError:
        print(f"SpaCy model '{spacy_model}' is not downloaded. Dowloading now - this might take a minute")
        from spacy.cli import download

        download(spacy_model)
        nlp = spacy.load(spacy_model)
    return nlp


class NormalizeNum:
    def __init__(self, nlp: spacy.language, locale_config: str):
        import locale

        locale.setlocale(locale.LC_ALL, locale_config)
        self.nlp = nlp
        self.atof = locale.atof
        self.stats = {
            "from a single number": 0,
            "from entities": 0,
            "from tokens": 0,
            "after normalization": 0,
            "from a range": 0,
        }

    @staticmethod
    def preprocess(text: str):
        # remove currency
        text = " ".join(regex.sub(r"\p{Sc}|(~)", " \g<0> ", text).split())
        # split any numbers attached to digits ("EUR19" -> "EUR 19")
        # return " ".join(regex.sub(r"(?:[A-Z]{3})(\d+)|(\d+)(?:[A-Z]{3})", " \g<0> ", text))
        text = regex.split(r"(?:[A-Z]{3})(\d+)|(\d+)(?:[A-Z]{3})", text)
        return " ".join(t for t in text if t)

    def extract_single_number(self, text: str) -> List[float]:
        try:
            # try extracting the number (in digits) directly (eg. "1,222")
            number = self.atof(text)
        except:
            try:
                # try extracting the number from words (eg. "two million")
                number = text2num(text, lang="en", relaxed=True)
            except:
                try:
                    # try normalizing the numbers to words, then extract the numbers
                    # (eg. "2 million" -> "two million" -> 2000000.0)
                    assert len(regex.findall(r"[0-9]+[,.]a?[0-9]*|[0-9]+", text)) == 1, BaseException
                    normalized_text = self.normalize_num(self.nlp(text), to_word=True)
                    number = text2num(normalized_text, lang="en", relaxed=True)
                except:
                    # handle decimals:
                    # if there is a decimal followed by a million/billion, etc
                    scales = ["hundred", "thousand", "million", "billion", "trillion"]
                    if len(regex.findall(r"[0-9]+[.]{1}[0-9]+", text)) == 1:
                        numbers = [token.text for token in self.nlp(text) if token.like_num]
                        if len(numbers) == 2 and len(set(numbers[1].split(" ")).intersection(scales)) != 0:
                            try:
                                return [self.atof(numbers[0]) * text2num(numbers[1], lang="en", relaxed=True)]
                            except BaseException:
                                raise BaseException
        return [number]

    def extract_numbers_from_tokens(self, doc: spacy.tokens.doc.Doc) -> List[float]:
        numbers = []
        tmp_num = ""
        num_ranges = []
        try:
            for i, token in enumerate(doc):
                if token.tag_ == "CD":
                    try:
                        num = self.normalize_num(token.text, to_word=True)
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
                        number = text2num(n, lang="en", relaxed=True)
                    numbers.append(number)

            return numbers
        except BaseException:
            raise BaseException

    @staticmethod
    def normalize_num(doc, to_word=False) -> str:
        new = ""
        for token in doc:
            if token.tag_ in ["CD", "SYM"]:
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

    def extract_numbers_from_entities(self, doc: spacy.tokens.doc.Doc, labels: List[str]) -> List[float]:
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
                transcribed_text = alpha2digit(new if new else ent.text, lang="en", ordinal_threshold=0, relaxed=True)
                if "MONEY" in labels and ent.label_ == "MONEY":
                    try:
                        return self.extract_numbers_from_tokens(doc)
                    except:
                        return self.extract_numbers_from_tokens(self.nlp(transcribed_text))

                try:
                    number = self.atof(transcribed_text)
                    numbers.append(number)
                except:
                    try:
                        normalized_num = self.normalize_num(self.nlp(transcribed_text), to_word=False)
                        numbers.append(self.atof(normalized_num))
                    except BaseException:
                        raise BaseException
        assert numbers != [], "No numbers extracted from entities"
        return numbers

    @staticmethod
    def _extract_spans(
        spans: List[dict[str, str | int]],
    ):
        return [(span["start"], span["end"]) for span in spans]

    def check_for_approximation(self, doc: spacy.tokens.doc.Doc, labels: List[str]) -> bool:
        tags = " ".join([token.tag_ for token in doc])
        ent_labels = [ent.label_ for ent in doc.ents]
        # check for any math symbols (>=, ~, etc) or if a number ends with a plus/plus-minus sign
        # or for combinations of a preposition, superlative, and number
        if "NFP" in tags or "IN JJS CD" in tags or ":" in tags or regex.findall(r"[0-9]+(\+|±)", doc.text):
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

    def extract_range(self, text: str) -> tuple[float]:
        text = self.normalize_num(self.nlp(text), to_word=False)
        nums = text.split("-")
        if len(nums) == 2:
            try:
                return (self.atof(nums[0]), self.atof(nums[1]))
            except:
                return None

    def extract_numbers(
        self,
        text: str,
        labels: List[str] = ["CARDINAL", "MONEY", "QUANTITY"],
    ) -> tuple[float | None, float | None, bool | None]:
        # text = text.strip().lower()
        # doc = nlp(text)
        text = self.preprocess(text)
        doc = self.nlp(text.strip())
        approx = self.check_for_approximation(doc, labels)

        try:
            # simplest approach, attempt to extract a single number
            self.stats["from a single number"] += 1
            numbers = self.extract_single_number(text)
        except BaseException:
            try:
                self.stats["from a range"] += 1
                numbers = self.extract_range(text)
                assert numbers, BaseException
            except BaseException:
                try:
                    # try extraction by spaCy NERs
                    self.stats["from entities"] += 1
                    numbers = self.extract_numbers_from_entities(doc, labels)
                except BaseException:
                    try:
                        # if no NERs were extacted or no NERs were useful, try extracting by token instead
                        self.stats["from tokens"] += 1
                        numbers = self.extract_numbers_from_tokens(doc)
                    except BaseException:
                        try:
                            # if all fails, try by normalizing the numbers to words
                            self.stats["after normalization"] += 1
                            doc = self.nlp(self.normalize_num(doc), to_words=True)
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

    def print_stats(self) -> None:
        import pprint

        pprint.pprint(self.stats, indent=3)


if __name__ == "__main__":
    examples = [
        "~ 30-400",
        "NT$34.5 million",
        "between 300 and 400",
        "300 and 400",
        "300-400",
        "300 - 400",
        "$1.1 million",
        "$5.1 million",
        "200,000+",
        "At least 60",
        "exactly 100",
        "just 2",
        "approximately 233",
        "At least 238 people died because of the heat, with 187 injuries.",
        "238 people died because of the heat, with 187 injuries.",  # okay parsing but wrong (due to injuries)
        "$692 million",
        "A$5 million",
        "$ six hundred ninety-two million",
        "A$ five million",
        "around 600 excess deaths in the United States, >=229 confirmed in the United States",
        "More than 2 lakhs (200 thousand) people have been affected",
        "between 9 and 66",
        "more than 1634 people",
        "no more than 1634",
        "$six hundred ninety-two million",
        "$ six hundred ninety-two million",
        "Apple is looking at buying U.K. startup for $1 billion",  # parses 1 billion as (1, 1bil)! problematic
        "two billion",
        "up to 12",
        "over 2,000 such visits",
        "exactly 1",
        ">= 200",
        "<55",
        "~4234",
        "~ 4234",
        "exactly 60",
        "almost 100",
        "no more than 13",
        "160 to say the least",
        "1,100 people were hospitalized",
        "More than 2,000",
        "More than 27,00,000",
        "337",
        "300 to 400 people",
        "hundreds of people",
        "11,000",
        "one death in Idaho",
        "12 missing",
        "EUR19 billion",
        "30-400",
    ]

    for i in examples:
        print(i)
        print(normalize.extract_numbers(i))
        print()

    print(normalize.print_stats())


# if __name__ == "__main__":
#     nlp = load_spacy_model("en_core_web_trf")
#     locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
#
#     test = extract_numbers(nlp(preprocess("NT$34.5 million")))
#     print(test)
#     print(type(test))
#     for i in test:
#         print(i, type(i))
#
#     test = extract_numbers(nlp(preprocess("300 - 400")))
#     print(test)
#     print(type(test))
#     for i in test:
#         print(i, type(i))
#
#     examples = [
#         "NT$34.5 million",
#         "between 300 and 400",
#         "300 and 400",
#         "300-400",
#         "300 - 400",
#         "$1.1 million",
#         "$5.1 million",
#         "200,000+",
#         "At least 60",
#         "exactly 100",
#         "just 2",
#         "approximately 233",
#         "At least 238 people died because of the heat, with 187 injuries.",
#         "238 people died because of the heat, with 187 injuries.",  # okay parsing but wrong (due to injuries)
#         "$692 million",
#         "A$5 million",
#         "$ six hundred ninety-two million",
#         "A$ five million",
#         "around 600 excess deaths in the United States, >=229 confirmed in the United States",
#         "More than 2 lakhs (200 thousand) people have been affected",
#         "between 9 and 66",
#         "more than 1634 people",
#         "no more than 1634",
#         "$six hundred ninety-two million",
#         "$ six hundred ninety-two million",
#         "Apple is looking at buying U.K. startup for $1 billion",  # parses 1 billion as (1, 1bil)! problematic
#         "two billion",
#         "up to 12",
#         "over 2,000 such visits",
#         "exactly 1",
#         ">= 200",
#         "<55",
#         "~4234",
#         "~ 4234",
#         "exactly 60",
#         "almost 100",
#         "no more than 13",
#         "160 to say the least",
#         "1,100 people were hospitalized",
#         "More than 2,000",
#         "More than 27,00,000",
#         "337",
#         "300 to 400 people",
#         "hundreds of people",
#         "11,000",
#         "one death in Idaho",
#         "12 missing",
#     ]
#     # nlp = load_spacy_model("en_core_web_trf")
#
#     #for i in examples:
#     #    i = preprocess(i)
#     #    print(i)
#     #    print(extract_numbers(nlp(i)))
#     #    print("--------------------------")
#
