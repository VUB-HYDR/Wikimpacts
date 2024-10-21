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


Based on the evaluation result of V3 cross these experiments, we select setting 2 for the further processing.
For the V4 and V5, we only use setting 2 for evaluation.

For double annotation, we have two annotators: one for the gold data and one for the output data. The annotator for the gold data worked prior to the implementation of the L1-3 guideline, while the annotator for the output data followed the new guideline. The L2 and L3 information in the gold data is extracted from the Location field. Information at the country level is assigned to L2, while sub-national level information is assigned to L3.
