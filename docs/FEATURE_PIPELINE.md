# Stage 1 — Feature Pipeline (`feature_fusion.py`)

Owner: **WS1 — Data Engineer**
Source: `src/pipeline/feature_fusion.py`
Config section: `feature_pipeline:` in `configs/default.yaml`

## What it does

Turns raw per-dataset netflow CSVs (CTU-13 today; CIC-IDS-2018 can be
added the same way) into one fused, normalized, sliding-windowed feature
table, ready for the Stage 2 graph builder.

```
load  →  clean  →  normalize  →  window  →  fuse  →  Parquet
```

1. **Load** — reads every dataset listed in `feature_pipeline.datasets`.
   If a file with "sample" in its name exists under a dataset's `raw_path`
   (e.g. `ctu13_sample.csv`), that's used for fast local runs; otherwise
   every `*.csv` under `raw_path` is loaded recursively and concatenated.
2. **Clean** — normalizes column names, drops duplicates, resolves a
   `Timestamp` column (from `StartTime` for CTU-13 if needed), coerces
   numeric-looking text columns to numbers, and fills missing values per
   `feature_pipeline.missing_value_strategy`.
3. **Normalize** — z-scores *continuous* numeric columns only. Categorical
   / ID-like numeric columns (ports, protocol numbers, TOS/state codes)
   and the label column are left untouched — see "Normalization
   exclusions" below. Per-column `{mean, std}` are written to
   `normalization.per_feature_stats_path` so the same normalization can
   be replayed later (e.g. at inference time) instead of recomputed.
4. **Window** — assigns each record to every **sliding** window it falls
   inside (see "Windowing" below), not just one.
5. **Fuse** — concatenates all datasets into one table, adding:
   - `entity_id` / `dst_entity_id` — source/destination node identifiers
     (from `SrcAddr`/`DstAddr` for CTU-13, `Src IP`/`Dst IP` for
     CIC-IDS-2018), which Stage 2 needs to build graph edges.
   - `source_dataset` — provenance, since different datasets have
     different schemas and get concatenated with NaN-filled
     non-overlapping columns.
6. Writes the result to `feature_pipeline.processed_output_path` (default
   `data/processed/features.parquet`).

## Config reference (`feature_pipeline:`)

| Key | Meaning |
|---|---|
| `window_size` | Width of each time window, in seconds. |
| `stride` | Spacing between window starts, in seconds. `window_size > stride` → overlapping windows. `window_size == stride` → non-overlapping. |
| `datasets` | List of `{name, raw_path}`. Add more entries to fuse multiple datasets. |
| `processed_output_path` | Directory for the output Parquet (and default location if no explicit path is passed to `run()`). |
| `normalization.method` | Only `z_score` is currently supported; anything else raises `NotImplementedError` at construction time. |
| `normalization.per_feature_stats_path` | Where per-column `{mean, std}` are saved as JSON. |
| `exclude_from_normalization` | Extra columns to exclude from z-scoring, on top of the engine's built-in defaults (ports, protocol, TOS, state, `window_id`). |
| `label_column` | Ground-truth label column name. Always excluded from numeric conversion and normalization. |
| `missing_value_strategy` | One of `forward_fill`, `zero_fill`, `mean_fill`. |
| `categorical_encoding` | Reserved for Stage 2/3 — not used by this stage yet. |

## Windowing (sliding, not tumbling)

A record at elapsed time `e` (seconds since the dataset's first
timestamp) belongs to **every** window `k` where:

```
k * stride <= e < k * stride + window_size
```

With the defaults (`window_size=60`, `stride=10`) a record lands in
~6 overlapping windows. This is intentional — each window becomes one
graph snapshot in Stage 2, and overlap is what lets the RSSM see gradual
state evolution rather than discrete jumps. If you want non-overlapping
windows instead, set `window_size == stride`.

## Normalization exclusions

Z-scoring is only meaningful for continuous features. The engine excludes,
by default: `Protocol`, `Proto`, `Dst Port`, `Src Port`, `Sport`, `Dport`,
`sTos`, `dTos`, `State`, `window_id`, plus whatever `label_column` is set
to. Add dataset-specific extras via `exclude_from_normalization` in the
config rather than editing the code.

## Output schema (beyond the original dataset columns)

| Column | Description |
|---|---|
| `Timestamp` | Parsed datetime (from `StartTime` if the raw data used that name). |
| `window_id` | Integer window index a row is assigned to (a row may appear once per overlapping window). |
| `window_start` | Datetime of that window's start. |
| `entity_id` | Source node identifier for the graph builder. |
| `dst_entity_id` | Destination node identifier for the graph builder. |
| `source_dataset` | Which configured dataset the row came from. |

## How to test

### Unit tests (recommended)

```bash
pip install pytest pyyaml pandas numpy pyarrow
pytest tests/test_pipeline.py -v
```

`tests/test_pipeline.py` loads the real `configs/default.yaml`, generates
synthetic CTU-13-style rows in a temp directory, and checks:
- the pipeline runs end-to-end and produces a non-empty Parquet file,
- sliding windows actually overlap (catches the `window_size`-ignored bug),
- categorical columns (`Proto`, `State`, ports) are **not** normalized,
- continuous columns (`Dur`, `TotPkts`, `TotBytes`) **are** normalized,
- `entity_id` / `dst_entity_id` are correctly pulled from CTU-13 columns,
- the label column survives untouched,
- `feature_stats.json` is written and excludes categoricals/label,
- bad config values (empty `datasets`, unknown `missing_value_strategy`)
  raise clear errors instead of failing silently downstream.

### Manual smoke test

```python
import yaml
from src.pipeline.feature_fusion import FeatureFusionEngine

with open("configs/default.yaml") as f:
    config = yaml.safe_load(f)

engine = FeatureFusionEngine(config["feature_pipeline"])
output_path = engine.run()

import pandas as pd
df = pd.read_parquet(output_path)
print(df.shape)
print(df[["entity_id", "dst_entity_id", "window_id"]].head())
```

Before running this for real, drop either a full CTU-13 export or a
small `ctu13_sample.csv` (a few hundred rows is enough) into
`data/raw/CTU-13/`.

## Known limitations / next steps

- Only CSV input is supported (no PCAP parsing).
- Only `z_score` normalization is implemented; `normalization.method`
  values other than `z_score` raise `NotImplementedError` by design —
  implement the branch in `normalize()` if you add another method.
- `categorical_encoding: embedding` in the config is a placeholder for
  Stage 2/3 — this stage doesn't encode categoricals itself.
- For very large `window_size / stride` ratios, the sliding-window
  `explode()` step multiplies row count accordingly — watch memory on
  full (non-sample) dataset runs.
