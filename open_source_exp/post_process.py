import collections
import json
import os
import pickle, re
from collections import defaultdict

import pandas as pd
import yaml


# Load the YAML data, allowing for duplicate keys
class UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = defaultdict(list)
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            value = self.construct_object(value_node, deep=deep)
            mapping[key].append(value)
        return dict(mapping)


def process_duplicates(d):
        new_dict = {}
        for key, value in d.items():
            if isinstance(value, list):
                for i, val in enumerate(value, start=1):
                    new_key = f"{key}{i}" if i > 1 else key
                    new_dict[new_key] = val
            else:
                new_dict[key] = value
        return new_dict


def preprocess_yaml_string(yaml_str):
    # This function will handle quoting and escaping in complex YAML strings

    # Escape double quotes inside the string values
    yaml_str = re.sub(r'(?<=: )"(.+?)"(?=,|$)', lambda m: '"' + m.group(1).replace('"', '\\"') + '"', yaml_str)

    # Add quotes around complex mappings if they are not already quoted
    yaml_str = re.sub(r'(?<=: )([^"\n\r]+)(?=\n|$)', r'"\1"', yaml_str)

    # Handle list items with colons inside quotes that might be misinterpreted
    def quote_colon_in_lists(match):
        parts = match.group(1).split(', ')
        quoted_parts = [f'"{part}"' if ':' in part else part for part in parts]
        return '- ' + ', '.join(quoted_parts)

    yaml_str = re.sub(r'- ([^:\n]+:[^:\n]+)', quote_colon_in_lists, yaml_str)

    return yaml_str

def convert_yaml_to_json(yaml_str):
    # Pre-process YAML string to remove lines without ":" and ignore specific YAML tags
    filtered_lines = []
    lines = [l for l in yaml_str.split("\n") if l ]
    for line in lines:
        if ":" in line and not line.startswith(" "):
            line = line.replace("\"", "").replace("'", "")
            parts = line.split(':')
            line = parts[0] + ": " + "\"" + "=".join(parts[1:]) + "\""
            if line.strip().startswith("-"):
                line = line.replace("-", " -")
            if line.strip():
                filtered_lines.append(line.replace("\"", "").replace("'", ""))
    processed_yaml_str = '\n'.join(filtered_lines)
    if not processed_yaml_str:
        return None
    try:
        data = yaml.load(processed_yaml_str, Loader=UniqueKeyLoader)
        print("YAML LOADED SUCCESSFULLY!")
    except Exception as e:
        print(e)
    processed_data = {}
    for key, value in data.items():
        if isinstance(value, dict):
            processed_data[key] = process_duplicates(value)
        else:
            processed_data[key] = value

    # Convert to JSON
    #json_str = json.dumps(processed_data, indent=4)
    return processed_data


def clean_json_string(input_str):
    # Regular expression to capture JSON objects and arrays
    json_pattern = re.compile(r'(\{.*?\}|\[.*?\])', re.DOTALL)

    # Use the regex to find all JSON objects and arrays
    json_objects = json_pattern.findall(input_str)

    # Try to parse each match as JSON to verify and clean it
    valid_json_parts = []
    for obj_str in json_objects:
        try:
            # Attempt to decode the JSON string
            json_obj = json.loads(obj_str)
            # If successful, convert it back to a JSON string for uniformity
            json_str = json.dumps(json_obj, ensure_ascii=False)
            valid_json_parts.append(json_str)
        except json.JSONDecodeError:
            # If error, continue without adding to the list
            continue

    # Join all valid JSON strings into one, separated by commas (consider if you need to encapsulate them in a list or another structure)
    cleaned_json = ",\n".join(valid_json_parts)

    return cleaned_json

def fix_json_format(json_string):
    # Fix unescaped backslashes and improperly quoted segments
    fixed_backslashes = json_string.replace('\\"', '\\\\"')
    # Fix malformed parts manually if necessary (e.g., excess brackets or parentheses)
    fixed_malformations = fixed_backslashes.replace('\\"")', '\\"}')
    return fixed_malformations

from dateparser.search import search_dates

def get_date(x):
    if isinstance(x, str):
        return x
    elif isinstance(x, dict):
        normalized_x = {}
        for k, v in x.items():
            normalized_x[k.strip().lower()] = str(v)
        day, month, year, date, time = None, None, None, None, None
        if "year" in normalized_x.keys():
            if "year" in normalized_x.keys():
                year = normalized_x["year"]
            if "month" in normalized_x.keys():
                month = normalized_x["month"]

            if "day" in normalized_x.keys():
                day = normalized_x["day"]

        elif "date" in normalized_x.keys():
            date = normalized_x["date"]
        elif "time" in normalized_x.keys():
            time = normalized_x["time"]
        else:
            for k in normalized_x.keys():
                text = search_dates(normalized_x[k], settings={'STRICT_PARSING': False, 'DATE_ORDER': 'DMY'})
                for x in text:
                    if x:
                        date_string = x[0]
                        date = date_string
                        break

        if year and month and day:
            result = f"{day}-{month}-{year}"
        elif year and month:
            result = f"{month}-{year}"
        elif year:
            result = year
        elif time:
            result = time
        elif date:
            result = date  # prefer date if present
        else:
            result = normalized_x
            print(normalized_x)
        return result


def extract_and_combine_json(input_text):
    # Pattern to extract JSON objects
    json_pattern = re.compile(r'\{[^{}]*\}')

    # Find all matches in the input text
    matches = json_pattern.findall(input_text)

    # Parse each JSON string into a Python dictionary and combine them
    combined_data = {}
    for json_str in matches:
        try:
            # Parse the JSON string
            data_part = json.loads(json_str)
            # Combine the parsed JSON into one dictionary
            combined_data.update(data_part)
        except json.JSONDecodeError:
            # Handle possible JSON decoding errors
            print(f"Skipping invalid JSON: {json_str}")

    return json.dumps(combined_data, indent=2)

if __name__ == "__main__":

    data_dir = "/home/murathan/PycharmProjects/Wikimpacts/open_source_exp/output/dev_gemma-2-9b-it"
    output_dir = data_dir.replace("output", "output_json").replace("raw", "raw_json")

    os.makedirs(output_dir, exist_ok=True)

    output_files = sorted([f for f in sorted(os.listdir(data_dir))  if ".pickle"  in f])
    print(len(output_files))
    fail_count = collections.defaultdict(int)
    except_count = 0
    for file_name in output_files:
        file_path = f"{data_dir}/{file_name}"
        # Load the JSON file
        json_dict = {}
        with open(file_path, 'rb') as file:
            #print(f)
            text = pickle.load(file)
            try:
                event_id = text["Event_ID"]
                url = text["URL"]
                event_name = text["Event_Name"]
                json_dict.update({"URL": url, "Event_ID": event_id,"Event_Name":  event_name, "prompt": text["prompt"]})
            except: pass
            for k, model_response in text.items():
                if k in ["URL", "Event_ID", "Event_Name", "prompt"]: continue
                if "gemma" in data_dir:
                    if "```json" in model_response:
                        model_response = model_response.split("```json")[-1].replace("```", "").strip()
                    if "model\n{" in model_response:
                        model_response = "{" + model_response.split("model\n{")[-1].strip()
                model_response = model_response.replace("\n", "").replace('\\_', '_')
                if model_response.strip().startswith("Here is") and '{' in model_response:
                    model_response = model_response[model_response.index("{"):]
                model_response = model_response.replace("<|eot_id|>", "").strip()
                try:
                    json_v = json.loads(model_response)
                except Exception as e:
                    try:
                        except_count+=1
                        if model_response.count("[") != model_response.count("]"):
                            model_response += "\"}]}"
                        if "Invalid \escape" in str(e):
                            model_response = model_response.encode('utf-8')
                            model_response = model_response.decode('unicode_escape')
                        elif "Expecting ',' delimiter" in str(e):
                            model_response = model_response + "}"
                            try: json.loads(model_response)
                            except: model_response = model_response + "}"
                        elif "I will provide" in model_response:
                            model_response = extract_and_combine_json(model_response)
                        else:
                            if "}" not in model_response:model_response = model_response + "\"}"
                            model_response = model_response[:model_response.rfind("}") + 1]
                            model_response = " ".join(model_response.split())
                            model_response = model_response.replace(", }", "}")
                        json_v = json.loads(model_response)
                    except Exception as e:
                            print(f"FAIL: {k}    {e}")
                            fail_count[k]+=1
                            #print(v, "\n")
                            continue
                if type(json_v) != dict:
                    continue
                json_dict.update(json_v)
        for x in ["Start_Date", "End_Date"]:
            if x in json_dict:
                if isinstance(json_dict[x], dict):
                    json_dict[x] = get_date(json_dict[x])
        with open(output_dir + "/" + file_name.replace(".pickle", ".json"), 'w', encoding='utf-8') as f_writer:
            json.dump(json_dict, f_writer, ensure_ascii=False, indent=4)

    print(f"Initially: {except_count}/{len(output_files)*13}")
    print(f"In the end: {sum(fail_count.values())}/{len(output_files)*13}")
    print(fail_count)
