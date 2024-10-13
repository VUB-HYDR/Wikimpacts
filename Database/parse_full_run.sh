#!/usr/bin/env bash

inputFilesDir=${1}
outputFilesDir=${2}

echo Input dir: ${inputFilesDir}
mkdir ${outputFilesDir}
echo Parsing files to output dir: ${outputFilesDir}

jsonChunks=(${inputFilesDir}/*)
prefix=".fixed.json"
lenJsonChunks=${#jsonChunks[@]}
echo "Found ${lenJsonChunks} chunks"

for chunk in "${jsonChunks[@]}"; do

    echo Fixing chunk ${chunk} for list of nums
    poetry run python3 Database/fix_json_inconsistencies.py -i ${chunk} -o ${chunk}${prefix} -n "data types and nested fields"
    echo Fixing chunk ${chunk} data types and nested fields
    poetry run python3 Database/fix_json_inconsistencies.py -i ${chunk}${prefix} -o ${chunk}${prefix} -n "list of nums"
    echo Parsing chunk ${chunk}${prefix}

    poetry run python3 Database/parse_events.py \
        --raw_dir ${inputFilesDir} \
        --filename $(basename ${chunk}${prefix}) \
        --output_dir ${outputFilesDir} \
        --event_levels l1,l2,l3 ||
        echo Parsing ${chunk}${prefix} has failed!!
done
