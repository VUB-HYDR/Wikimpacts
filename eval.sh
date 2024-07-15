#!/bin/bash

# Check if enough arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 EXPERIMENT_NAME MODEL_NAME DATA_SPLIT"
    exit 1
fi

# Assign arguments to variables
EXPERIMENT_NAME=$1
MY_MODEL=$2
DATA_SPLIT=$3
WEIGHTS_CONFIG="nlp4climate"
if [[ $DATA_SPLIT == "dev" ]]; then
  GOLD_FILE="/home/murathan/PycharmProjects/Wikimpacts/Database/gold/gold_dev_20240515.parquet"
else
  GOLD_FILE="/home/murathan/PycharmProjects/Wikimpacts/Database/gold/gold_test_20240515.parquet"
fi

# Define directories
INPUT_DIR="Database/raw/$EXPERIMENT_NAME"
OUTPUT_DIR="Database/raw/$EXPERIMENT_NAME/merged/"
PARSED_OUTPUT_DIR="Database/output/$EXPERIMENT_NAME"
EVALUATION_OUTPUT_DIR="Database/evaluation_results/$EXPERIMENT_NAME"

# Step to merge JSON files if there are multiple output files
echo "Merging JSON files..."
poetry run python Database/merge_json_output.py \
  --input_dir $INPUT_DIR \
  --output_dir $OUTPUT_DIR \
  --model_name $MY_MODEL

# Parse events
PARQUET_FILE="$PARSED_OUTPUT_DIR/${MY_MODEL}.parquet"
if [ ! -f "$PARQUET_FILE" ]; then
echo "Parsing events..."
poetry run python Database/parse_events.py \
  --raw_dir $OUTPUT_DIR \
  --filename "${MY_MODEL}.json" \
  --output_dir $PARSED_OUTPUT_DIR \
  --event_type main
fi

# Evaluation step
echo "Evaluating model output..."
poetry run python Evaluation/evaluator.py \
  --sys-file "$PARSED_OUTPUT_DIR/${MY_MODEL}.parquet" \
  --gold-file "$GOLD_FILE" \
  --model-name "$EXPERIMENT_NAME/$DATA_SPLIT" \
  --null-penalty 1 \
  --score all \
  --weights_config $WEIGHTS_CONFIG

echo "Evaluation complete. Check the results in $EVALUATION_OUTPUT_DIR/$DATA_SPLIT"
