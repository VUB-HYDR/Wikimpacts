#!/usr/bin/env bash

for file in Database/raw/WikimpactsV2/fullrun/single_events/*.json; do 
    filename=$(basename "$file")
    echo file name: $filename
  
    
    poetry run python3 Database/parse_events.py \
        -r Database/raw/WikimpactsV2/fullrun/single_events \
        -f "$filename" \
        -o Database/output/WikimpactsV2/fullrun/single_event \
        -lvl l1,l3 \
       # echo Parsing $filename has failed!!
done
