#!/usr/bin/env bash

inputFilesDir=${1}
outputFilesDir=${1}

echo Input dir: ${inputFilesDir}
mkdir ${outputFilesDir}
echo Parsing files to output dir: ${outputFilesDir}

jsonChunks=(${inputFilesDir}/*)

lenJsonChunks=${#jsonChunks[@]}
echo "Found ${lenJsonChunks} chunks"

for chunk in "${jsonChunks[@]}"; do
    echo "Parsing ${chunk}"
    poetry run python3 Database/parse_events.py \
    --raw_dir ${inputFilesDir} \
    --filename $(basename ${chunk}) \
    --output_dir ${outputFilesDir} \
    --event_levels l1,l2,l3 \
    || echo "Parsing ${chunk}" has failed!!
done
