import locale

import regex
import spacy
from num2words import num2words
from text_to_num import alpha2digit, text2num

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
spacy_model = "en_core_web_trf"

try:
    nlp = spacy.load(spacy_model, enable=["transformer", "ner", "tagger"])
    print(f"SpaCy model '{spacy_model}' has been loaded")
except OSError:
    print(f"SpaCy model '{spacy_model}' is not downloaded. Dowloading now - this might take a minute")
    from spacy.cli import download

    download(spacy_model)
    nlp = spacy.load(spacy_model)


def extract_single_number(text: str) -> list[float] | None:
    try:
        # try extracting the number directly
        number = locale.atof(text)
        return [number]
    except:
        try:
            # try extracting the number from wordsf
            number = text2num(text, lang="en", relaxed=True)
            return [number]
        except BaseException as err:
            try:
                # try normalizing the numbers to words, then extract the numbers
                # TODO: generalize to strings that may have multiple numbers in words
                text = normalize_num_to_words(nlp(text))
                number = text2num(text, lang="en", relaxed=True)
                return [number]
            except BaseException as err:
                # print("SINGLE: Could not parse numbers,", err)
                raise BaseException


def extract_numbers_from_tokens(doc: spacy.tokens.doc.Doc) -> list[float]:
    numbers = []
    try:
        for token in doc:
            if token.tag_ == "CD":
                numbers.append(locale.atof(token.text))
        return numbers
    except BaseException as err:
        print("TOKEN: Could not parse numbers,", err)
        raise BaseException


def normalize_num_to_words(doc) -> str:
    new = ""
    for token in doc:
        if token.tag_ == "CD" or token.tag_ != "$":
            try:
                new += num2words(token.text)
                if token.whitespace_:
                    new += token.whitespace_
            except:
                new += token.text
                if token.whitespace_:
                    new += token.whitespace_
    # remove "and"
    new = regex.sub(r"(and)[\s]", "", new)

    # remove leftover currency not detected by spaCy
    new = regex.sub(r"\p{Sc}", "", new)
    return new


def extract_numbers_from_entities(doc: spacy.tokens.doc.Doc, labels: list[str] = ["CARDINAL", "MONEY", "QUANTITY"]):
    numbers = []
    if not doc.ents:
        raise BaseException
    for ent in doc.ents:
        if ent.label_ in labels:
            # in case any numbers are spelled out, transcribe them
            transcribed_text = alpha2digit(ent.text, lang="en", ordinal_threshold=0, relaxed=True)
            if "MONEY" in labels and ent.label_ == "MONEY":
                try:
                    return extract_numbers_from_tokens(doc)
                except:
                    return extract_numbers_from_tokens(nlp(transcribed_text))
            try:
                # if the transcribed version is parsable,
                # it was most likely not an approximation
                number = locale.atof(transcribed_text)
                numbers.append(number)
            except BaseException as err:
                # print("ENT: Could not parse numbers,", err)
                raise BaseException

    return numbers


def check_for_inequality_symbol(doc) -> bool:
    tags = [token.tag_ for token in doc]
    return True if "NFP" in tags else False


def extract_numbers(text: str):
    print(text)
    approx = None
    text = text.strip().lower()
    try:
        numbers = extract_single_number(text)
        approx = False
        # print("extract_single_number", numbers, approx)

    except BaseException:
        # pprint.pprint(doc.to_json(), indent=3)
        doc = nlp(text)
        try:
            # try extraction by spaCy ner
            numbers = extract_numbers_from_entities(doc)
            approx = check_for_inequality_symbol(doc)
            # print("extract_numbers_from_entities", numbers, approx)
        except BaseException:
            try:
                # try extracting by token
                numbers = extract_numbers_from_tokens(doc)
                approx = True
                # print("extract_numbers_from_tokens", numbers, approx)
            except BaseException:
                try:
                    # if all fails, try by normalizing the numbers to words
                    doc = nlp(normalize_num_to_words(doc))
                    numbers = extract_numbers_from_entities(doc)
                    approx = check_for_inequality_symbol(doc)
                    # print("EXTRACTED NUMBERS (BaseException)")
                except BaseException:
                    return (None, None, None)

    if numbers:
        numbers = sorted(numbers)
        if len(numbers) == 1:
            return (numbers[0], numbers[0], approx)
        elif len(numbers) == 2:
            return (numbers[0], numbers[1], approx)
    print("EXTRACTED NUMBERS:", numbers)
    return (None, None, approx)


if __name__ == "__main__":
    examples = [
        "$692 million",  # ignores the million
        "$ six hundred ninety-two million",
        ">= 200",
        "<55",
        "~4234",
        "~ 4234",
        "no more than 1634",  # considers this as an approx
        "more than 1634 people",
        "up to 12",  # PROPBLEM WITH IN
        "238 people died because of the heat, with 187 injuries.",  # okay parsing but wrong (due to injuries)
        "between 9 and 66",  # is this approx?
        "exactly 60",
        "approximately 233",
        "almost 100",
        "no more than 13",
        "160 to say the least",
        "over 2,000 such visits",  # not approx?  PROPBLEM WITH IN
        "1,100 people were hospitalized",
        "around 600 excess deaths in the United States, >=229 confirmed in the United States",  # extracts too many numbers
        "At least 60",
        "Apple is looking at buying U.K. startup for $1 billion",  # does not parse as 1 billion
        "two billion",
        "At least 238 people died because of the heat, with 187 injuries.",  # extracts too many numbers
        "More than 2,000",
        "More than 27,00,000",
        "337",
        "300 to 400 people",
        "hundreds of people",
        "A$5 million",  # australian dollars, can't parse
        "A$ five million",  # australian dollars, can't parse
        "$six hundred ninety-two million",
        "$ six hundred ninety-two million",  # i removed text2num.... this is why this won't work
        "More than 2 lakhs (200 thousand) people have been affected",  # extracts 4 nums
        "11,000",
        "one death in Idaho",
        "12 missing",
    ]

    # working_with = ["A$ five million", "A$5 million", "A$ 5 million"]
    print("MIN", "MAX", "APPROX?")
    for i in examples:
        # find all currency symbols
        i = " ".join(regex.sub(r"\p{Sc}|(~)", " \g<0> ", i).split())
        # i = " ".join(regex.sub(r"\p{Sm}|\p{Sc}", " \g<0> ", i).split())

        print(extract_numbers(i))
        print("--------------------------")
