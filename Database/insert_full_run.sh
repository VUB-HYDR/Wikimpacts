#!/usr/bin/env bash

##################
# This bash script inserts levels of all events (l1, l2, and l3) in one go
# The files must exist in a certain tree format.
# Here is an example with some categories:
# .
# ├── l1
# │   └── 0000.parquet
# ├── l2
# │   ├── Instance_Per_Administrative_Areas_Affected
# │   │   ├── 0000.parquet
# │   │   ├── 0001.parquet
# │   │   ├── ...
# │   │   └── 0034.parquet
# │   ├── Instance_Per_Administrative_Areas_Buildings_Damaged
# │   │   └── 0000.parquet
# │   ├── Instance_Per_Administrative_Areas_Displaced
# │   │   ├── 0000.parquet
# │   │   ├── 0001.parquet
# │   │   ├── ...
# │   │   └── 0201.parquet
# │   └── Instance_Per_Administrative_Areas_Damage
# │       ├── 0000.parquet
# │       ├── 0001.parquet
# │       ├── ...
# │       └── 0345.parquet
# └── l3
#     ├── Specific_Instance_Per_Administrative_Area_Affected
#     │   ├── 0000.parquet
#     │   └── 0001.parquet
#     ├── Specific_Instance_Per_Administrative_Area_Buildings_Damaged
#     │   ├── 0000.parquet
#     │   ├── 0001.parquet
#     │   └── 0002.parquet
#     ├── Specific_Instance_Per_Administrative_Area_Deaths
#     │   ├── 0000.parquet
#     │   ├── 0001.parquet
#     │   ├── ...
#     │   └── 0103.parquet
#     └── Specific_Instance_Per_Administrative_Area_Injuries
#         └── 0000.parquet
#
# Note 1: All categories are supported! Any other directories are ignroed!
# Note 2: Rows that could not be inserted due to some Integrity Error are stored in /tmp/
###################

levels=("l1" "l2" "l3")
inputFilesDir=${1}
dbName=${2}
nidPath=${3}
dryRun=${4}
saveOutput=${5}
saveOutputDir=${6}

echo Input: ${inputFilesDir}
echo Target database: ${dbName} - NOTE: will be ignored if dryRun!
echo Nids will be stored in ${nidPath}

for lvl in "${levels[@]}"; do
    echo Processing ${lvl}

    if [[ ${lvl} == "l1" ]]
    then

        if [[ -n ${saveOutputDir} ]]
            then
                saveOutputDirLvl=${saveOutputDir}/${lvl}
                echo Storing output in ${saveOutputDirLvl}
        fi
        poetry run python3 Database/insert_events.py -m append -f ${inputFilesDir}/${lvl} -db ${dbName} -lvl ${lvl} -gj -nid ${nidPath} ${dryRun} ${saveOutput} ${saveOutputDirLvl}
    else
        for filePath in ${inputFilesDir}/${lvl}/*; do

            echo File Path ${filePath}
            tblName=$(basename $filePath)
            echo Table Name ${tblName}

            if [[ -n ${saveOutputDir} ]]
                then
                    saveOutputDirLvl=${saveOutputDir}/${lvl}/${tblName}
                    echo Storing output in ${saveOutputDirLvl}
            fi

            poetry run python3 Database/insert_events.py -m "append" -f ${filePath}  -db ${dbName} -lvl ${lvl} -t ${tblName} -gj -nid ${nidPath} ${dryRun} ${saveOutput} ${saveOutputDirLvl}
        done
    fi
done

if [[ ${dryRun} != "-d" && ${dryRun} != "--dry_run"]]
then
    echo Inserting geojson to table GeoJson_Obj
    poetry run python3 Database/schema/populate_geojson_table.py -db ${dbName} -tbl Database/schema/geojson_tbl.sql -f ${nidPath}/geojson
fi
