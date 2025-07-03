#!/usr/bin/env bash
#count=0
for file in Database/raw/WikimpactsV2/fullrun/multi_events/*.json; do 
   
    #count=$((count + 1))
    #if [ "$count" -lt 7 ]; then
    #    continue
    #fi
    filename=$(basename "$file")
    echo file name: $filename
    
    poetry run python3 Database/parse_events.py \
        -r Database/raw/WikimpactsV2/fullrun/multi_events\
        -f "$filename" \
        -o Database/output/WikimpactsV2/fullrun/multi_events \
        -lvl l1,l3 \
       # echo Parsing $filename has failed!!
done
