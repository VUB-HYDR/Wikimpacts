# Releases:

## Dev

| Database    | Description |
| -------- | ------- |
| [releases/impact.v0.db](releases/impact.v0.db)  | A **preliminary database**, contains development data as proof-of-concept |

## Raw

| Database    | Description |
| [releases/impactdb.v1.0.raw.db](releases/impactdb.v1.0.raw.db)  | A **raw database** before applying a final layer of post-processing to ensure consistency across all levels. In this release, currencies and inflation adjustment years are mixed. The database contains data after parsing LLM output but before applying: (a) data gap filling (see #173 and #101), and (2) currency conversion and inflation adjustment to USD (2024) (see #111). |
| [releases/impactdb.v1.1.raw.db](releases/impactdb.v1.1.raw.db)  | A **raw database** that improves on [releases/impactdb.v1.0.raw.db](releases/impactdb.v1.0.raw.db) by adding stricter validation. |
| [releases/impactdb.v1.2.raw.db](releases/impactdb.v1.2.raw.db)  | A **raw database** that improves on [releases/impactdb.v1.1.raw.db](releases/impactdb.v1.0.raw.db) that fixes a major bug in raw=<v.1.1 where None/NULL values end up inside the databases in non-nullable columns |
| [releases/impactdb.v1.3.raw.db](releases/impactdb.v1.3.raw.db) **LATEST** | A **raw database** that modifies the schema of [releases/impactdb.v1.2.raw.db](releases/impactdb.v1.0.raw.db) so that end years of events are nullable.  |

## Data-Gap Filled

| [releases/impactdb.v1.0.dg_filled.db](releases/impactdb.v1.0.dg_filled.db)  | A **post-processed** database after applying a final layer of post-processing, excluding the handling of currencies and inflation adjustment (has missing validation rules) |
| [releases/impactdb.v1.1.dg_filled.db](releases/impactdb.v1.1.dg_filled.db) | A **post-processed** database after applying a final layer of post-processing, including the handling of currencies and inflation adjustment. In this release, end years of events are nullable. |
| [releases/impactdb.v1.2.dg_filled.db](impactdb.v1.2.dg_filled.db) **Inflation to 2024 USD version** | A **post-processed** database that improves on [releases/impactdb.v1.1.dg_filled.db](impactdb.v1.1.dg_filled.db) by removing events that have no L1/L2/L3 impacts (ie. all impact data in L1 is NULL), most currencies are converted to USD in the database and inflated to 2024 value. |
| [releases/impactdb.v1.3.dg_filled.db](impactdb.v1.3.dg_filled.db) **Inflation to 2024 EUR version** | A **post-processed** database that convert 2024 USD to 2024 EUR on [releases/impactdb.v1.2.dg_filled.db](impactdb.v1.2.dg_filled.db) by using a constant conversion rate in 2024 |

### Additional files and metadata
| File    | Description |
| -------- | ------- |
| `*_insertion_errors` files in [releases](releases) | Database insertion errors in addition to the post-processing log file if present -- the version is in the filename |
| [Database/output/full_run_25_deduplicated](Database/output/full_run_25_deduplicated) | Processed LLM output corresponding to database `impactdb.v1.*.raw.db`|
| [Database/output/full_run_25_deduplicated_data_gap](Database/output/full_run_25_deduplicated_data_gap) | Processed LLM output corresponding to database `impactdb.v1.*.dg_filled.db`|
| [full_run_25_deduplicated](full_run_25_deduplicated) | A directory containing all unique instances of GeoJson objects. These are inserted into the databases (`raw` and `dg_filled`) in the table `GeoJson_Obj` if present. |

### Notes

- The diff between the latest `raw` and the latest `dg-filled` databases represents all the fixed inconsistencies. The number of records may differ.
- For more details, check the GitHub release page: https://github.com/VUB-HYDR/Wikimpacts/releases
