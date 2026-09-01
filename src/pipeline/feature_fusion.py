"""
feature_fusion.py
==================
Stage 1 of the CyberDream pipeline: Feature Pipeline (WS1).

Loads CIC-IDS-2018 / CTU-13 flow data, cleans it, normalizes
numeric features, creates sliding time windows, and saves a Parquet file.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# Columns that should never be treated as continuous numeric features,
# even if pandas infers a numeric dtype for them (they're categorical /
# identifier-like and z-scoring them would destroy their meaning for
# the downstream graph encoder).
DEFAULT_NORMALIZATION_EXCLUDE = {
    "Protocol",
    "Proto",
    "Dst Port",
    "Src Port",
    "Source Port",
    "Destination Port",
    "sTos",
    "dTos",
    "window_id",
}

# Candidate column names (case-insensitive) for source / destination
# identifiers across CIC-IDS-2018 and CTU-13 schemas.
SRC_ID_CANDIDATES = ["src ip", "source ip", "srcaddr", "src_addr", "saddr"]
DST_ID_CANDIDATES = ["dst ip", "destination ip", "dstaddr", "dst_addr", "daddr"]


class FeatureFusionEngine:
    """
    Handles ingestion, cleaning, normalization, sliding-windowing,
    and fusion of raw network flow records from CIC-IDS-2018 / CTU-13.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    # ------------------------------------------------------------------
    # Stage 1a: Load
    # ------------------------------------------------------------------
    def load_raw_sources(self, raw_dir: Path) -> dict[str, pd.DataFrame]:
        """
        Load CSV files from the raw dataset directory.

        For fast local testing, sample files (cic2018_sample.csv /
        ctu13_sample.csv) are used if present instead of loading the
        full original datasets. Otherwise every *.csv found anywhere
        under raw_dir (including nested day-wise subfolders, which is
        how CIC-IDS-2018 is typically distributed) is loaded.
        """

        raw_dir = Path(raw_dir)
        if not raw_dir.exists():
            raise FileNotFoundError(f"Raw data directory not found: {raw_dir}")

        records: dict[str, pd.DataFrame] = {}

        sample_map = {
            "CIC-IDS-2018": raw_dir / "cic2018_sample.csv",
            "CTU-13": raw_dir / "ctu13_sample.csv",
        }

        for source_name, sample_file in sample_map.items():
            if sample_file.exists():
                print(f"Loading sample: {sample_file}")
                records[source_name] = pd.read_csv(sample_file, low_memory=False)

        if records:
            return records

        # Fall back to loading every CSV under raw_dir (recursive, to
        # cover CIC-IDS-2018's day-wise subfolder layout and CTU-13's
        # per-scenario subfolder layout).
        csv_files = sorted(raw_dir.rglob("*.csv"))

        if not csv_files:
            raise FileNotFoundError(
                f"No CSV files found in {raw_dir} (checked recursively). "
                f"Place CIC-IDS-2018 / CTU-13 files under data/raw/<dataset>/."
            )

        for csv_file in csv_files:
            print(f"Loading: {csv_file.relative_to(raw_dir)}")
            # Use the immediate parent dataset folder name when available
            # so files from different scenario subfolders don't collide.
            key = csv_file.parent.name if csv_file.parent != raw_dir else csv_file.stem
            df = pd.read_csv(csv_file, low_memory=False)
            if key in records:
                records[key] = pd.concat([records[key], df], ignore_index=True)
            else:
                records[key] = df

        return records

    # ------------------------------------------------------------------
    # Stage 1b: Clean
    # ------------------------------------------------------------------
    def clean(self, raw_records: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Clean raw records:
        - remove duplicate rows
        - clean column names
        - convert StartTime/Timestamp
        - convert numeric columns
        - handle missing numeric values
        """

        cleaned = {}

        for source_name, df in raw_records.items():

            df = df.copy()

            # Clean column names
            df.columns = (
                df.columns
                .str.strip()
                .str.replace(r"\s+", " ", regex=True)
            )

            # Remove duplicate rows
            df = df.drop_duplicates()

            # Convert CTU-13 StartTime to common Timestamp column
            if "StartTime" in df.columns and "Timestamp" not in df.columns:
                df["Timestamp"] = pd.to_datetime(df["StartTime"], errors="coerce")

            # Convert Timestamp
            if "Timestamp" in df.columns:
                df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
                before = len(df)
                df = df.dropna(subset=["Timestamp"])
                dropped = before - len(df)
                if dropped:
                    print(f"  {source_name}: dropped {dropped} rows with unparseable Timestamp")
            else:
                raise ValueError(
                    f"'{source_name}' has no Timestamp/StartTime column — "
                    "windowing requires a time column."
                )

            if df.empty:
                raise ValueError(
                    f"'{source_name}' has no valid rows left after Timestamp "
                    "cleaning — check the raw file's date format."
                )

            # Convert possible numeric columns (skip Label/time columns)
            for column in df.columns:

                if column in ["Timestamp", "StartTime", "Label"]:
                    continue

                if df[column].dtype == "object":

                    converted = pd.to_numeric(df[column], errors="coerce")

                    # Convert only when most values are numeric
                    valid_ratio = converted.notna().mean()

                    if valid_ratio > 0.8:
                        df[column] = converted

            # Replace infinity values
            df = df.replace([np.inf, -np.inf], np.nan)

            # Forward fill followed by zero fill (numeric columns only,
            # so we don't zero-fill a missing Label / identifier by mistake)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].ffill().fillna(0)

            cleaned[source_name] = df

            print(f"Cleaned {source_name}: {df.shape[0]} rows, {df.shape[1]} columns")

        return cleaned

    # ------------------------------------------------------------------
    # Stage 1c: Normalize
    # ------------------------------------------------------------------
    def normalize(self, cleaned_records: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Apply z-score normalization to continuous numeric features only.

        Timestamp, StartTime, Label, and configured categorical/ID-like
        numeric columns (ports, protocol numbers, etc.) are left unchanged.
        """

        exclude = set(DEFAULT_NORMALIZATION_EXCLUDE)
        exclude.update(self.config.get("exclude_from_normalization", []))

        normalized = {}

        for source_name, df in cleaned_records.items():

            df = df.copy()

            numeric_columns = [
                c for c in df.select_dtypes(include=[np.number]).columns
                if c not in exclude
            ]

            for column in numeric_columns:

                mean = df[column].mean()
                std = df[column].std()

                if pd.isna(std) or std == 0:
                    df[column] = 0.0
                else:
                    df[column] = (df[column] - mean) / std

            normalized[source_name] = df

            print(f"Normalized {source_name}: {len(numeric_columns)} numeric columns")

        return normalized

    # ------------------------------------------------------------------
    # Stage 1d: Sliding window
    # ------------------------------------------------------------------
    def window(self, normalized_records: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Assign each record to every sliding window it falls inside.

        A record at elapsed time `e` belongs to window `k` (window start
        = k * stride) whenever:  k*stride <= e < k*stride + window_size

        With window_size == stride this reduces to the old non-overlapping
        behaviour; with window_size > stride, records correctly appear in
        multiple overlapping windows, which is what `window_size` is
        supposed to control.
        """

        window_size = int(self.config.get("window_size", 60))
        stride = int(self.config.get("stride", 10))

        if window_size <= 0 or stride <= 0:
            raise ValueError("window_size and stride must both be positive.")

        windowed = {}

        for source_name, df in normalized_records.items():

            df = df.copy()

            if "Timestamp" not in df.columns:
                raise ValueError("Timestamp column is required for windowing.")

            start_time = df["Timestamp"].min()
            elapsed = (df["Timestamp"] - start_time).dt.total_seconds().to_numpy()

            # For each record, compute the inclusive range of window
            # indices [k_min, k_max] whose window it falls inside.
            k_max = np.floor(elapsed / stride).astype(int)
            k_min = np.maximum(0, np.ceil((elapsed - window_size) / stride)).astype(int)

            df["window_id"] = [
                np.arange(lo, hi + 1) for lo, hi in zip(k_min, k_max)
            ]

            # A record now spans one row per overlapping window.
            df = df.explode("window_id", ignore_index=True)
            df["window_id"] = df["window_id"].astype(int)

            df["window_start"] = start_time + pd.to_timedelta(
                df["window_id"] * stride, unit="s"
            )

            windowed[source_name] = df

            print(
                f"Windowed {source_name}: {df['window_id'].nunique()} windows "
                f"(window_size={window_size}s, stride={stride}s), "
                f"{df.shape[0]} row-window assignments"
            )

        return windowed

    # ------------------------------------------------------------------
    # Stage 1e: Fuse
    # ------------------------------------------------------------------
    def fuse_sources(self, windowed_records: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Merge all sources into one feature table.

        Adds `entity_id` / `dst_entity_id` (source and destination node
        identifiers, needed by the Stage 2 graph builder to create edges)
        and `source_dataset` (provenance, since CIC-IDS-2018 and CTU-13
        have different schemas and get concatenated with NaN-filled
        non-overlapping columns).
        """

        frames = []

        for source_name, df in windowed_records.items():

            df = df.copy()
            df["source_dataset"] = source_name

            if "entity_id" not in df.columns:
                df["entity_id"] = self._extract_id(df, SRC_ID_CANDIDATES, default=source_name)

            if "dst_entity_id" not in df.columns:
                df["dst_entity_id"] = self._extract_id(df, DST_ID_CANDIDATES, default=None)

            frames.append(df)

        if not frames:
            raise ValueError("No records available for fusion.")

        fused = pd.concat(frames, ignore_index=True, sort=False)

        return fused

    @staticmethod
    def _extract_id(df: pd.DataFrame, candidates: list[str], default: str | None) -> pd.Series:
        """Find the first matching column (case-insensitive) among candidates."""
        lower_map = {c.lower(): c for c in df.columns}
        for candidate in candidates:
            if candidate in lower_map:
                return df[lower_map[candidate]].astype(str)
        return pd.Series([default] * len(df), index=df.index)

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------
    def run(self, raw_dir: Path, output_path: Path) -> Path:
        """
        Run complete feature pipeline:
        load -> clean -> normalize -> window -> fuse -> Parquet.
        """

        print("\n=== CyberDream Feature Pipeline ===")

        raw_records = self.load_raw_sources(raw_dir)
        cleaned = self.clean(raw_records)
        normalized = self.normalize(cleaned)
        windowed = self.window(normalized)
        fused = self.fuse_sources(windowed)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fused.to_parquet(output_path, index=False)

        print("\n=== Pipeline Complete ===")
        print(f"Output: {output_path}")
        print(f"Shape: {fused.shape}")

        return output_path
