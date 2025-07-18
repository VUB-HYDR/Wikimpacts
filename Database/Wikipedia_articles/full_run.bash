#!/usr/bin/env bash
counter=1
for file in Database/Wikipedia_articles/multi_events_full_run/*.json; do
  filename=$(basename "$file")
  poetry run python3 Database/Prompts/run_prompts_v2.py \
    -r Database/Wikipedia_articles/multi_events_full_run \
    -f "$filename" \
    --api_env .env \
    --prompt_category all \
    -a multi \
    -b Database/Prompts/batch \
    -d "multi_events_full_run$counter"
  ((counter++))
done