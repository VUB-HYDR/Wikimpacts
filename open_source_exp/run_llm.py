import os
import pickle
import shutil
import sys
import time

from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch
from prompts_original_updated import prompts
from config import key

login(token=key)
device = "cuda"  # the device to load the model onto


def load_model(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if "Mixtral-8x7B" in model_name:
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True,
        )
        model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=bnb_config, device_map="auto")
        return tokenizer, model
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            attn_implementation="flash_attention_2"
        )
        return tokenizer, model


def run_prompt(article_path, tokenizer, model, prompts):
    with open(article_path, 'rb') as file:
        data = pickle.load(file)

    info_box = data["info_box"]
    text = data["text"]
    event_name = data["event_name"]
    url = data["URL"]
    event_id = data["Event_ID"]
    data_for_prompt = {
        "info_box": info_box,
        "Whole_text": text,
        "Event_Name": event_name
    }
    max_new_tokens=8192
    results = {"Event_Name": event_name, "URL": url, "Event_ID": event_id}
    for prompt_name, prompt_template in prompts.items():
        prompt = prompt_template.format_map(data_for_prompt)
        messages = [
            {"role": "user", "content": prompt},
        ]
        input_ids = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(model.device)

        if "llama" in model.name_or_path:
            terminators = [
                tokenizer.eos_token_id,
                tokenizer.convert_tokens_to_ids("<|eot_id|>")
            ]
            generated_ids = model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                eos_token_id=terminators,
                do_sample=False,
            )
            decoded = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
            decoded = decoded[0].split("<|end_header_id|>")[-1].strip("<|eot_id|").strip()
        else:
            generated_ids = model.generate(input_ids, max_new_tokens=max_new_tokens, do_sample=False)
            decoded = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
            decoded = decoded[0]
        results["prompt"] = prompt
        results[prompt_name] = decoded
    return results


if __name__ == "__main__":
    model_option = sys.argv[1]
    split = sys.argv[2]
    model_map = {
        "gemma9b": "google/gemma-2-9b-it",
        "gemma27b": "google/gemma-2-27b-it",
        "llama8": "meta-llama/Meta-Llama-3-8B-Instruct",
        "llama70": "meta-llama/Meta-Llama-3-70B-Instruct",
        "climate7": "eci-io/climategpt-7b",
        "llama2-7": "meta-llama/Llama-2-7b-chat",
        "climate13": "eci-io/climategpt-13b",
        "llama2-13": "meta-llama/Llama-2-13b-chat",
        "llama3.1-8": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    }

    model_name = model_map.get(model_option)
    if model_name is None:
        print("Wrong model ID")
        exit()
    model_basename = model_name.split("/")[-1]

    tokenizer, model = load_model(model_name)
    print(f"Running the model {model_name} on {split} split")

    exclude_files = [
        "2014 Southeast Europe floods.pickle",
        "2021 Western North America heat wave.pickle",
        "2022 European heatwaves.pickle",
        "Hurricane Agnes.pickle",
        "Hurricane_Danielle_(2022).pickle",
        "Hurricane Elsa.pickle",
        "Hurricane Floyd.pickle",
        "Hurricane Ophelia (2005).pickle",
        "Hurricane_Polo_(2014).pickle",
        "southeast Australia Bushfires.pickle",
        "Tropical Storm Erika.pickle",
        "Tropical_Storm_Haiyan_(2007).pickle",
        "Tropical_Storm_Jerry_(2001).pickle",
        "Typhoon_Mawar_(2005).pickle"
    ]

    articles_directory = f'preprocessed_articles/{split}'
    prompt_dict = prompts
    save_dir = f"output/{split}_{model_basename}"
    try:
        shutil.rmtree(save_dir)
    except:
        pass
    os.makedirs(save_dir, exist_ok=True)

    for filename in sorted(os.listdir(articles_directory)):
        start_time = time.time()
        print(filename)
        if filename not in exclude_files:
            continue
        if filename.endswith('.pickle'):
            article_path = os.path.join(articles_directory, filename)
            output_path = os.path.join(save_dir, filename)
            if os.path.exists(output_path):
                print(f"Skipping {output_path} as it exists!")
                continue
            # Process the article with each prompt
            try:
                processed_results = run_prompt(article_path, tokenizer, model, prompt_dict)
            except Exception as e:
                print("Exception", e)
                continue
            # Save the results to a JSON file
            with open(output_path, 'wb') as json_file:
                pickle.dump(processed_results, json_file)
            print(f'Processed and saved results for {filename} . it took {time.time() - start_time} seconds. \n')
