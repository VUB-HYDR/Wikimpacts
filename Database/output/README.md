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
