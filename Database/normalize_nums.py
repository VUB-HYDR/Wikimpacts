import locale

import regex
import spacy
from num2words import num2words
from text_to_num import alpha2digit, text2num

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

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

def extract_single_number(text: str) -> list[float]:
    try:
        # try extracting the number (in digits) directly (eg. "1,222")
        number = locale.atof(text)
    except:
        try:
            # try extracting the number from words (eg. "two million")
            number = text2num(text, lang="en", relaxed=True)
            return [number]
        except BaseException as err:
            try:
                # try normalizing the numbers to words, then extract the numbers
                # (eg. "2 million" -> "two million" -> 2000000.0)
                text = normalize_num_to_words(nlp(text))
                number = text2num(text, lang="en", relaxed=True)
            except BaseException as err:
                print("SINGLE: Could not parse numbers,", err)
                raise BaseException
    return [number]


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


def extract_numbers_from_entities(doc: spacy.tokens.doc.Doc, labels: list[str] = ["CARDINAL", "MONEY", "QUANTITY"]) -> list[float]:
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
                pass
                #raise BaseException
    assert numbers != [], "No numbers extracted from entities"
    return numbers


def check_for_inequality_symbol(doc) -> bool:
    # TODO: the assumption now is that inequality symbols and other math symbols are extracted as NFP by spaCy
    # But I think the name of the function should change (check for comparatives or inequalities) or something 
    # and it should grab whatever is before and after the CD block (for robustness, maybe whatever is before the 
    # first CD and after the last CD, since there are often multiple numbers or a number over a longer span - or potentially
    # using the spaCy ent span instead)
    # Then, if any JJR/JJS/NFP exists, it's most likely an estimation 
    tags = [token.tag_ for token in doc]
    return True if "NFP" in tags else False


def extract_numbers(text: str) -> tuple[float|None, float|None, float|None]:
    print(text)
    approx = None
    text = text.strip().lower()
    try:
        # simplest approach, attempt to extract a single number
        numbers = extract_single_number(text)
        # assume that extracted numbers are not an approximation
        approx = False
        # print("extract_single_number", numbers, approx)

    except BaseException:
        # pprint.pprint(doc.to_json(), indent=3)
        # if extracting a single number fails:
        doc = nlp(text)
        try:
            # try extraction by spaCy NERs
            numbers = extract_numbers_from_entities(doc)

            # an approx if an inequality symbol exists (>=, ~, etc)
            approx = check_for_inequality_symbol(doc)
            # print("extract_numbers_from_entities", numbers, approx)
        except BaseException:
            try:
                # if no NERs were extacted or no NERs were useful, try extracting by token instead
                numbers = extract_numbers_from_tokens(doc)

                # usually, the chosen spaCy model tends to have a longer span for CD 
                # if the number is an approximation (such as in 'at least 30 people')
                # so we'll assume it's an approximation
                approx = True
                # print("extract_numbers_from_tokens", numbers, approx)
            except BaseException:
                try:
                    # if all fails, try by normalizing the numbers to words
                    doc = nlp(normalize_num_to_words(doc))
                    numbers = extract_numbers_from_entities(doc)

                    # an approx if an inequality symbol exists (>=, ~, etc)
                    # TODO: this could probably be refactored to be done at an earlier stage and determine the approx based on it 
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
        "$692 million",
        "$ six hundred ninety-two million",
        ">= 200",
        "<55",
        "~4234",
        "~ 4234",
        "no more than 1634",  # considers this as an approx
        "more than 1634 people",
        "up to 12",  # PROPBLEM WITH 'IN'
        "238 people died because of the heat, with 187 injuries.",  # okay parsing but wrong (due to injuries)
        "between 9 and 66",  # is this approx? I think not
        "exactly 60",
        "approximately 233",
        "almost 100",
        "no more than 13",
        "160 to say the least",
        "over 2,000 such visits",  # not approx?  PROPBLEM WITH 'IN'
        "1,100 people were hospitalized",
        "around 600 excess deaths in the United States, >=229 confirmed in the United States",
        "At least 60",
        "Apple is looking at buying U.K. startup for $1 billion",  # parses 1 billion as (1, 1bil)! problematic
        "two billion",
        "At least 238 people died because of the heat, with 187 injuries.",
        "More than 2,000",
        "More than 27,00,000",
        "337",
        "300 to 400 people",
        "hundreds of people",
        "A$5 million", # parses 5 million as (5, 1mil)! problematic
        "A$ five million", 
        "$six hundred ninety-two million",
        "$ six hundred ninety-two million",
        "More than 2 lakhs (200 thousand) people have been affected", # problem with "thousand"
        "11,000",
        "one death in Idaho",
        "12 missing",
    ]

    nlp = load_spacy_model("en_core_web_trf")

    print("MIN", "MAX", "APPROX?")
    for i in examples:
        # find all currency symbols and space them out
        i = " ".join(regex.sub(r"\p{Sc}|(~)", " \g<0> ", i).split())
        print(extract_numbers(i))
        print("--------------------------")
