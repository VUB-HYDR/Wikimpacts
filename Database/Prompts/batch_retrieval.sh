#!/usr/bin/env bash
counter=3
count=0
for file in Database/Wikipedia_articles/full_run_single_events_2.0/*.json; do
 
  count=$((count + 1))
  if [ "$count" -lt 3 ]; then
    continue
  fi
  filename=$(basename "$file")
  poetry run python3 Database/Prompts/batch_output_retrivel.py\
    -r Database/Wikipedia_articles/full_run_single_events_2.0 \
    -f "$filename" \
    --api_env .env \
    -t single \
    -m o3-mini-2025-01-31\
    -o Database/raw/WikimpactsV2/fullrun/single_events\
    -d "single_event_full_run$counter"
  ((counter++))
done