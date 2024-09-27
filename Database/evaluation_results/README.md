For ESSD_2024 folders, we use the same name as the output folder, but add the experiment name in the end.
The "filter" means that the records are with L2 and L3 annotation.
ESSD_2024_V3_filter_dft is the evaluation result under the default setting
In total we have 5 experiments, and the settings are listed as below
experiment & Weight & Threshold & NULL Penalty \
default & 1.0 for all & 0.6 & 0.5\
setting1 & 1.0 for non-nullable items, 0.125 for nullable items & 0.6 & 0.5 \
setting2 & 1.0 for non-nullable items, 0.125 for nullable items & 0.6 & 1.0 \
setting3 & 1.0 for non-nullable items, 0.125 for nullable items & 0.6 & 0.0 \
setting4 & 1.0 for non-nullable items, 0.125 for nullable items & 0.0 & 1.0 \
setting 5 & 1.0 for location, 0 for others & 0.6 & 1.0 \

Based on the evaluation result of V3 cross these experiments, we select setting 2 for the further processing.
For the V4 and V5, we only use setting 2 for evaluation.
