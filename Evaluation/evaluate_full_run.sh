#!/usr/bin/env bash

##################
# This bash script evaluates all event levels (l1, l2, and l3) in one go
# The goldFileDir and sysFileDir must exist in a certain tree format as shown below:

# GOLD FILE DIR
# ├── l1
# │   └── Total_Summary.parquet
# ├── l2
# │   ├── Instance_Per_Administrative_Areas_Affected.parquet
# │   ├── Instance_Per_Administrative_Areas_Buildings_Damaged.parquet
# │   ├── Instance_Per_Administrative_Areas_Damage.parquet
# │   ├── Instance_Per_Administrative_Areas_Deaths.parquet
# │   ├── Instance_Per_Administrative_Areas_Displaced.parquet
# │   ├── Instance_Per_Administrative_Areas_Homeless.parquet
# │   └── Instance_Per_Administrative_Areas_Injuries.parquet
# └── l3
#     ├── Specific_Instance_Per_Administrative_Area_Affected.parquet
#     ├── Specific_Instance_Per_Administrative_Area_Buildings_Damaged.parquet
#     ├── Specific_Instance_Per_Administrative_Area_Damage.parquet
#     ├── Specific_Instance_Per_Administrative_Area_Deaths.parquet
#     ├── Specific_Instance_Per_Administrative_Area_Displaced.parquet
#     ├── Specific_Instance_Per_Administrative_Area_Homeless.parquet
#     ├── Specific_Instance_Per_Administrative_Area_Injuries.parquet
#     └── Specific_Instance_Per_Administrative_Area_Insured_Damage.parquet
#
# SYS FILE DIR
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
###################

levels=("l1" "l2" "l3")
monetary_impacts=("Damage" "Insured_Damage")
numerical_impacts=("Deaths" "Injuries" "Affected" "Buildings_Damaged" "Homeless" "Displaced")
goldFileDir=${1}
sysFileDir=${2}
dataSplit=${3}
dataSplit_sys=${4}
outputDir=${5}
matcherNullPenalty=0.5
matcherThreshold=0.6

echo Gold Directory: ${goldFileDir}
echo System Output Directory: ${sysFileDir}

for lvl in "${levels[@]}"; do
    if [[ ${lvl} == "l1" ]]; then
        echo Evaluating ${lvl}
        poetry run python3 Evaluation/evaluator.py \
            --sys_output ${sysFileDir}/${dataSplit_sys}/${lvl} \
            --gold_set ${goldFileDir}/${dataSplit}/${lvl} \
            --model_name ${outputDir}/${dataSplit}/${lvl} \
            --null_penalty 1 \
            --score all \
            --weights_config ESSD_2024_${lvl} \
            --event_level ${lvl} \
            --matcher_null_penalty ${matcherNullPenalty} \
            --matcher_threshold ${matcherThreshold}


    else
        for filePath in ${goldFileDir}/${dataSplit}/${lvl}/*; do
            echo Evaluating ${lvl}
            for mi in "${monetary_impacts[@]}"; do
                if [[ ${lvl} == "l2" ]]; then
                    targetImpact=Instance_Per_Administrative_Areas_${mi}
                else
                    targetImpact=Specific_Instance_Per_Administrative_Area_${mi}
                fi
                echo Skipping impact ${targetImpact}
                # TODO: implement this after fixing evalution of monetary impact categories
                # poetry run python3 Evaluation/evaluator.py \
                #     --sys_output ${sysFileDir}/${dataSplit}/${lvl}/${targetImpact} \
                #     --gold_set ${goldFileDir}/${dataSplit}/${lvl}/${targetImpact}.parquet \
                #     --model_name ${outputDir}/${dataSplit}/${lvl} \
                #     --null_penalty 1 \
                #     --score all \
                #     --weights_config ESSD_2024_${lvl}_monetary \
                #     --event_level ${lvl} \
                #     --impact_type ${targetImpact}
                #     --matcher_null_penalty ${matcherNullPenalty} \
                #     --matcher_threshold ${matcherThreshold}
            done
            for ni in "${numerical_impacts[@]}"; do
                if [[ ${lvl} == "l2" ]]; then
                    targetImpact=Instance_Per_Administrative_Areas_${ni}
                else
                    targetImpact=Specific_Instance_Per_Administrative_Area_${ni}
                fi

                echo Evaluating impact ${targetImpact}
                poetry run python3 Evaluation/evaluator.py \
                    --sys_output ${sysFileDir}/${dataSplit_sys}/${lvl}/${targetImpact} \
                    --gold_set ${goldFileDir}/${dataSplit}/${lvl}/${targetImpact}.parquet \
                    --model_name ${outputDir}/${dataSplit}/${lvl} \
                    --null_penalty 1 \
                    --score all \
                    --weights_config ESSD_2024_${lvl}_numerical \
                    --event_level ${lvl} \
                    --impact_type ${targetImpact} \
                    --matcher_null_penalty ${matcherNullPenalty} \
                    --matcher_threshold ${matcherThreshold}
            done
        done
    fi
done
