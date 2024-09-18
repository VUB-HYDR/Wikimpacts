#!/usr/bin/env bash

levels=("l2" "l3") # l1
monetary_impacts=("Damage" "Insured_Damage")
numerical_impacts=("Deaths" "Injuries" "Affected" "Buildings_Damaged" "Homeless" "Displaced")
goldFileDir=${1}
sysFileDir=${2}
dataSplit=${3}

echo Gold Directory: ${goldFileDir}
echo System Output Directory: ${sysFileDir}

for lvl in "${levels[@]}"; do
    if [[ ${lvl} == "l1" ]]; then
        echo Evaluating ${lvl}
        poetry run python3 Evaluation/evaluator.py \
            --sys_output ${sysFileDir}/${dataSplit}/${lvl} \
            --gold_set ${goldFileDir}/${dataSplit}/${lvl} \
            --model_name essd/${dataSplit}/${lvl} \
            --null_penalty 1 \
            --score all \
            --weights_config ESSD_2024_${lvl} \
            --event_level ${lvl}


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
                #     --model_name essd/${dataSplit}/${lvl} \
                #     --null_penalty 1 \
                #     --score all \
                #     --weights_config ESSD_2024_${lvl}_monetary \
                #     --event_level ${lvl} \
                #     --impact_type ${targetImpact}
            done
            for ni in "${numerical_impacts[@]}"; do
                if [[ ${lvl} == "l2" ]]; then
                    targetImpact=Instance_Per_Administrative_Areas_${ni}
                else
                    targetImpact=Specific_Instance_Per_Administrative_Area_${ni}
                fi

                echo Evaluating impact ${targetImpact}
                poetry run python3 Evaluation/evaluator.py \
                    --sys_output ${sysFileDir}/${dataSplit}/${lvl}/${targetImpact} \
                    --gold_set ${goldFileDir}/${dataSplit}/${lvl}/${targetImpact}.parquet \
                    --model_name essd/${dataSplit}/${lvl} \
                    --null_penalty 1 \
                    --score all \
                    --weights_config ESSD_2024_${lvl}_numerical \
                    --event_level ${lvl} \
                    --impact_type ${targetImpact}
            done
        done
    fi
done
