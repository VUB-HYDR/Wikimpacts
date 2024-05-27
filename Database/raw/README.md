#### Raw output from LLMs

Suggested breakdown:

```shell
.
├── README.md # <-- ℹ️ You are here
└── nlp4climate # <-- ℹ️ Broader name to group experiments
    ├── sys1_outputs # <-- ℹ️ The name of the system + `_output` as a suffix
    │   ├── test.json
    │   └── dev.json
    └── sys2_outputs
        ├── dev_sys2_7B.json
        ├── dev_sys2_30B.json
        ├── test_sys2_7B.json
        └── test_sys2_30B.json
```

----
#### TODO: add schema
#### TODO: add schema + json validator
#### TODO: add script to merge mixtral models (or model outputs over several files)
