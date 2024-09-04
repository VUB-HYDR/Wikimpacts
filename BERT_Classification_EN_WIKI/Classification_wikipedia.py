# -*- coding: utf-8 -*-

import argparse

import pandas as pd
import torch
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast

from Database.scr.normalize_utils import Logging

if __name__ == "__main__":
    logger = Logging.get_logger("classification training")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--raw_dir",
        dest="raw_dir",
        help="The directory containing the training data",
        type=str,
    )

    args = parser.parse_args()
    logger.info(f"Passed args: {args}")
    # Load the dataset to inspect its structure
    filepath = f"{args.raw_dir}/'shuffled_training_dataset.csv'"
    df = pd.read_csv(filepath)

    # Manual splitting
    train_df = df[:150]  # First 100 records for training
    validation_df = df[150:250]  # Next 100 records for validation
    evaluation_df = df[250:]  # Last 100 records for evaluation

    model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)
    # Initialize the tokenizer
    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

    # Ensure the Whole_Text column is a string and drop any rows with NaN values in 'Whole_Text'
    train_df = train_df.dropna(subset=["Whole_Text"]).astype({"Whole_Text": "str"})
    validation_df = validation_df.dropna(subset=["Whole_Text"]).astype({"Whole_Text": "str"})
    evaluation_df = evaluation_df.dropna(subset=["Whole_Text"]).astype({"Whole_Text": "str"})

    # Now, tokenize again with the cleaned data
    train_encodings = tokenizer(train_df["Whole_Text"].tolist(), truncation=True, padding=True, max_length=512)
    val_encodings = tokenizer(validation_df["Whole_Text"].tolist(), truncation=True, padding=True, max_length=512)
    test_encodings = tokenizer(evaluation_df["Whole_Text"].tolist(), truncation=True, padding=True, max_length=512)

    from torch.utils.data import Dataset

    class WikipediaDataset(Dataset):
        def __init__(self, encodings, labels):
            self.encodings = encodings
            self.labels = labels

        def __getitem__(self, idx):
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item["labels"] = torch.tensor(self.labels[idx])
            return item

        def __len__(self):
            return len(self.labels)

    # Create dataset objects
    train_dataset = WikipediaDataset(train_encodings, train_df["Relevance"].tolist())
    val_dataset = WikipediaDataset(val_encodings, validation_df["Relevance"].tolist())
    test_dataset = WikipediaDataset(test_encodings, evaluation_df["Relevance"].tolist())

    from transformers import Trainer, TrainingArguments

    # Define training arguments
    training_args = TrainingArguments(
        output_dir="./results",  # Directory where the results will be saved
        num_train_epochs=10,  # Total number of training epochs
        per_device_train_batch_size=8,  # Batch size per device during training
        per_device_eval_batch_size=8,  # Batch size for evaluation
        warmup_steps=500,  # Number of warmup steps for learning rate scheduler
        weight_decay=0.01,  # Strength of weight decay
        logging_dir="./logs",  # Directory for storing logs
        logging_steps=10,
        evaluation_strategy="epoch",  # Evaluate the model at the end of each epoch
    )

    # Initialize the Trainer
    trainer = Trainer(
        model=model,  # The instantiated 🤗 Transformers model to be trained
        args=training_args,  # Training arguments, defined above
        train_dataset=train_dataset,  # Training dataset
        eval_dataset=val_dataset,  # Evaluation dataset
    )

    import torch

    trainer.train()

    from transformers import EarlyStoppingCallback

    trainer.add_callback(EarlyStoppingCallback(early_stopping_patience=2))

    # Define the path where you want to save the model
    # Replace 'my_model' with your desired model name
    model_save_path = "./DistilBertForSequenceClassification_WIKI_Natural_disaster"

    # Save the model and tokenizer using the `save_pretrained` method
    model.save_pretrained(model_save_path)
    tokenizer.save_pretrained(model_save_path)
