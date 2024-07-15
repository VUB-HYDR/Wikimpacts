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
    else: # model_name == "mistralai/Mistral-7B-Instruct-v0.2":
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
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
                max_new_tokens=2000,
                eos_token_id=terminators,
                do_sample=False,
            )
            decoded = tokenizer.batch_decode(generated_ids, skip_special_tokens= True)
            decoded = decoded[0].split("<|end_header_id|>")[-1].strip("<|eot_id|").strip()
        else:

            generated_ids = model.generate(input_ids, max_new_tokens=2000, do_sample=False)
            decoded = tokenizer.batch_decode(generated_ids, skip_special_tokens= True)
            decoded = decoded[0].split("[/INST]")[-1].strip("</s>").strip()
        results["prompt"] = prompt
        results[prompt_name] = decoded
    return results


if __name__ == "__main__":
    model_option = sys.argv[1]
    split = sys.argv[2]
    if "mistral" in model_option:
        print("No Mistral!")
        exit()
    elif "gemma9b" in model_option:
        model_name = "google/gemma-2-9b-it"
    elif "gemma7b" in model_option:
        model_name = "google/gemma-2-27b-it"
    elif "llama8" in model_option:
        model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
    elif "llama70" in model_option:
        model_name = "meta-llama/Meta-Llama-3-70B-Instruct"
    else:
        print("Wrong model ID")
        exit()
    model_basename = model_name.split("/")[-1]

    tokenizer, model = load_model(model_name)

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
        if filename.endswith('.pickle'):
            article_path = os.path.join(articles_directory, filename)
            # Process the article with each prompt
            try:
                processed_results = run_prompt(article_path, tokenizer, model, prompt_dict)
            except Exception as e:
                print("Exception", e)
                continue
            # Save the results to a JSON file
            output_filename = filename.replace('.txt', '.pickle')
            output_path = os.path.join(save_dir, output_filename)
            with open(output_path, 'wb') as json_file:
                pickle.dump(processed_results, json_file)
            print(f'Processed and saved results for {filename} . it took {time.time() - start_time} seconds. \n')
