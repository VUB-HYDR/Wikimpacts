# -*- coding: utf-8 -*-


import argparse

import pandas as pd
import torch
from torch.nn.functional import softmax
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Replace 'your-username/your-model-name' with the actual model path on Hugging Face
model = AutoModelForSequenceClassification.from_pretrained(
    "liniiiiii/DistilBertForSequenceClassification_WIKI_Natural_disaster"
)
tokenizer = AutoTokenizer.from_pretrained("liniiiiii/DistilBertForSequenceClassification_WIKI_Natural_disaster")


from Database.scr.normalize_utils import Logging

if __name__ == "__main__":
    logger = Logging.get_logger("classification training")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--filename",
        dest="filename",
        help="The name of the csv file containing Wikipedia articles in the <raw_dir> directory",
        type=str,
    )
    parser.add_argument(
        "-r",
        "--file_dir",
        dest="file_dir",
        help="The directory containing the raw file and the classified output file",
        type=str,
    )
    args = parser.parse_args()
    logger.info(f"Passed args: {args}")
    # File paths
    wiki_articles_path = f"{args.file_dir}/{args.filename}"  # Replace with your file path

    # Load the dataset
    df = pd.read_csv(wiki_articles_path)

    # Prepare the model for evaluation
    model.eval()

    def classify_text(text):
        if not isinstance(text, str):
            text = str(text)  # Convert to string if not already

        # Split the text into segments of 512 tokens
        tokenized_text = tokenizer.encode_plus(text, add_special_tokens=True, truncation=True, max_length=512)

        # Process each segment and aggregate results (you can adjust this part)
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        probabilities = softmax(outputs.logits, dim=-1)
        prediction = torch.argmax(probabilities, dim=-1).item()
        return prediction

    # Classify each text in the dataset
    results = []
    for _, row in df.iterrows():
        prediction = classify_text(row["Whole_Text"])
        results.append({"source": row["Source"], "prediction": prediction})

    # Create a new DataFrame for the results
    results_df = pd.DataFrame(results)

    # Save the results to a new CSV file
    results_df.to_csv(f"{args.file_dir}/{args.filename.replace('.csv', '_classified.csv')}", index=False)
