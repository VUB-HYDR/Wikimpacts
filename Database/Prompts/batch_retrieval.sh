#!/usr/bin/env bash
counter=1
for file in Database/Wikipedia_articles/multi_events_full_run/*.json; do
  filename=$(basename "$file")
  poetry run python3 Database/Prompts/batch_output_retrivel.py\
    -r Database/Wikipedia_articles/multi_events_full_run \
    -f "$filename" \
    --api_env .env \
    -t multi \
    -m o3-mini-2025-01-31\
    -o Database/output/WikimpactsV2/fullrun/multi_events\
    -d "multi_events_full_run$counter"
  ((counter++))
done