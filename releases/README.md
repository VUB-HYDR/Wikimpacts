## Releases:

| Database    | Description |
| -------- | ------- |
| [releases/impact.v0.db](releases/impact.v0.db)  | A **preliminary database**, contains development data as proof-of-concept |
| [releases/impactdb.v1.0.raw.db](releases/impactdb.v1.0.raw.db)  | A **raw database** before applying a final layer of post-processing to ensure consistency across all levels. In this release, currencies and inflation adjustment years are mixed |
| [releases/impactdb.v1.1.raw.db](releases/impactdb.v1.1.raw.db)  | A **raw database** that improves on [releases/impactdb.v1.0.raw.db](releases/impactdb.v1.0.raw.db) by tackling various bugs (has missing validation rules) |
| [releases/impactdb.v1.2.raw.db](releases/impactdb.v1.2.raw.db)  | A **raw database** that improves on [releases/impactdb.v1.1.raw.db](releases/impactdb.v1.0.raw.db) by tackling various bugs (has missing validation rules) |
| [releases/impactdb.v1.0.dg_filled.db](releases/impactdb.v1.0.dg_filled.db)  | A **post-processed** database after applying a final layer of post-processing, excluding the handling of currencies and inflation adjustment (has missing validation rules) |

### Additional files and metadata
| File    | Description |
| -------- | ------- |
| `*_insertion_errors` files in [releases](releases) | Database insertion errors in addition to the post-processing log file if present -- the version is in the filename |
| [Database/output/full_run_25_deduplicated](Database/output/full_run_25_deduplicated) | Processed LLM output corresponding to database `impactdb.v1.*.raw.db`|
| [Database/output/full_run_25_deduplicated_data_gap](Database/output/full_run_25_deduplicated_data_gap) | Processed LLM output corresponding to database `impactdb.v1.*.dg_filled.db`|
| [full_run_25_deduplicated](full_run_25_deduplicated) | A directory containing all unique instances of GeoJson objects. These are inserted into the databases (`raw` and `dg_filled`) in the table `GeoJson_Obj` if present. |
