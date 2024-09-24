In the evaluation process, we first get the evaluation results of the different settings of matching algorithm for L2 and L3, in which we have 5 settings of matcher.py as shown in the table below
  Name & Weight  & Threshold & NULL Penalty \\
      default& 1.0 for all & 0.6 & 0.5\\
     setting1 &  1.0 for non-nullable items, 0.125 for nullable items & 0.6 & 0.5 \\
     setting2 &  1.0 for non-nullable items, 0.125 for nullable items & 0.6 & 1.0 \\
     setting3 &  1.0 for non-nullable items, 0.125 for nullable items  & 0.6 & 0.0 \\
      setting4 & 1.0 for non-nullable items, 0.125 for nullable items  & 0.0 & 1.0 \\
And we evaluate the settings above using V3 output. Since in the dev set, we only have 54 events with L2/L3 annotation, therefore, the evaluation is based on these events.

Next, we have 3 versions of prompts test in the process, and we test them using the 54 events for L1/L2/L3
 Prompt version  & Description \\
       V3  & For the impact categories, all questions in the one prompt \\
       V4 & For the impact categories, L1 and L2 related questions in the one prompt, and L3 related questions in one prompt \\
       V5 & For the impact categories, L1, L2 and L3 related questions in three prompts respectively. \\
