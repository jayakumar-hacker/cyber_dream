# CyberDream — Feature Pipeline (WS1)

## Overview

The Feature Fusion Pipeline is Stage 1 (WS1) of the CyberDream project.

It converts raw network-flow CSV data into a cleaned, normalized, time-windowed feature table and stores the result as a Parquet file.

## Supported Datasets

- CIC-IDS-2018
- CTU-13

## Pipeline Flow

```text
Raw network-flow CSV
        ↓
Load data
        ↓
Clean data
        ↓
Remove duplicates
        ↓
Timestamp conversion
        ↓
Handle missing / infinite values
        ↓
Numeric feature conversion
        ↓
Z-score normalization
        ↓
Time-window creation
        ↓
Feature fusion
        ↓
Parquet output
```

## Main Implementation

The pipeline is implemented in:

```text
src/pipeline/feature_fusion.py
```

The main class is `FeatureFusionEngine`.

### Processing stages

1. `load_raw_sources()` — loads CSV files.
2. `clean()` — cleans columns, removes duplicates, converts timestamps/numeric fields, and handles missing values.
3. `normalize()` — applies z-score normalization to numeric features.
4. `window()` — creates time windows using the configured window size and stride.
5. `fuse_sources()` — combines processed records into one feature table.
6. `run()` — executes the complete pipeline and writes the Parquet output.

## Configuration

Configuration is stored in:

```text
configs/default.yaml
```

| Setting | Value |
|---|---|
| Window size | 60 seconds |
| Stride | 10 seconds |
| Normalization | Z-score |
| Missing-value strategy | Forward fill |
| CTU-13 raw path | `data/raw/CTU-13/` |
| Processed output directory | `data/processed/` |

## Output

Processed datasets are stored as:

```text
data/processed/ctu13_features.parquet
data/processed/cic2018_features.parquet
```

Parquet is used for efficient storage and loading of large processed feature tables.

## Validation

### CTU-13

- Raw flow data was converted to CSV.
- Feature Fusion completed successfully.
- Output: `ctu13_features.parquet`
- Verified shape: approximately `19,976,700 × 19`
- Missing-value check: `0`

### CIC-IDS-2018

- Feature Fusion completed successfully.
- Output: `cic2018_features.parquet`
- The same cleaning, normalization, and windowing pipeline was tested.

## GitHub Update

The following files were updated:

```text
src/pipeline/feature_fusion.py
configs/default.yaml
```

The changes were committed and pushed to the `main` branch.

Commit:

```text
8af71dc
```

Commit message:

```text
Update feature pipeline and configuration
```

## Current Status

**Feature Pipeline / WS1: COMPLETE**

The Feature Fusion implementation and configuration have been tested and pushed to the repository.

## Next Stage

Graph construction (WS2) is a separate stage and is not included in this Feature Fusion implementation.
