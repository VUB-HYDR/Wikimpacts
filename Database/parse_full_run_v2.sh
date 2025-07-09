#!/usr/bin/env bash

for file in Database/raw/WikimpactsV2/fullrun/multi_events/table_list/filter/4_10/*.json; do 
   
    #count=$((count + 1))
    #if [ "$count" -lt 21 ]; then
       # continue
    #fi
    filename=$(basename "$file")
    echo file name: $filename
    
    poetry run python3 Database/parse_events.py \
        -r Database/raw/WikimpactsV2/fullrun/multi_events/table_list/filter/4_10\
        -f "$filename" \
        -o Database/output/WikimpactsV2/fullrun/multi_events/table_list_4_10 \
        -lvl l1,l3 \
       # echo Parsing $filename has failed!!
done
