#### Post-processed files

This is where parsed LLM outputs are stored in .parquet

Suggested breakdown:

```shell
.
├── README.md # <-- ℹ️ You are here
└── nlp4climate # <-- ℹ️ Broader name to group experiments
    ├── dev # <-- ℹ️ dev set, specific to this group of experiments
    │   ├── gpt4_experiment.parquet
    │   └── mistral_experiment.parquet
    └── test # <-- ℹ️ test set, specific to this group of experiments
        ├── gpt4_experiment.parquet
        └── mistral_experiment.parquet
```


For ESSD_2024, we have different folders for storing the parsed output

ESSD_2024_V3 is the folder for the result from V3 prompts and other versions (V4, V5, etc).

ESSD_2024_V3_filter, is the folder for the result from V3 prompts except that we filter out the events without L2/L3 annotations. We do the same for other versions (V4, V5, etc)
