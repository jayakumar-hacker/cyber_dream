"""
feature_fusion.py
==================
Stage 1 of the CyberDream pipeline: Feature Pipeline (WS1).

Loads CIC-IDS-2018 / CTU-13 flow data, cleans it, normalizes
numeric features, creates time windows, and saves a Parquet file.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


class FeatureFusionEngine:
    """
    Handles ingestion, cleaning, normalization, windowing,
    and fusion of raw network flow records.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def load_raw_sources(self, raw_dir: Path) -> Any:
        """
        Load CSV files from the raw dataset directory.

        For initial testing, if cic2018_sample.csv exists,
        it is used instead of loading the very large original files.
        """

        raw_dir = Path(raw_dir)

        sample_file = raw_dir / "cic2018_sample.csv"

        if sample_file.exists():
            print(f"Loading sample: {sample_file}")
            df = pd.read_csv(sample_file)
            return {"CIC-IDS-2018": df}

        csv_files = sorted(raw_dir.glob("*.csv"))

        if not csv_files:
            raise FileNotFoundError(
                f"No CSV files found in {raw_dir}"
            )

        records = {}

        for csv_file in csv_files:
            print(f"Loading: {csv_file.name}")
            records[csv_file.stem] = pd.read_csv(csv_file)

        return records

    def clean(self, raw_records: Any) -> Any:
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
                df["Timestamp"] = pd.to_datetime(
                    df["StartTime"],
                    errors="coerce"
                )

            # Convert Timestamp
            if "Timestamp" in df.columns:
                df["Timestamp"] = pd.to_datetime(
                    df["Timestamp"],
                    errors="coerce"
                )

                df = df.dropna(subset=["Timestamp"])

            # Convert possible numeric columns
            for column in df.columns:

                if column in ["Timestamp", "StartTime", "Label"]:
                    continue

                if df[column].dtype == "object":

                    converted = pd.to_numeric(
                        df[column],
                        errors="coerce"
                    )

                    # Convert only when most values are numeric
                    valid_ratio = converted.notna().mean()

                    if valid_ratio > 0.8:
                        df[column] = converted

            # Replace infinity values
            df = df.replace(
                [np.inf, -np.inf],
                np.nan
            )

            # Forward fill followed by zero fill
            df = df.ffill().fillna(0)

            cleaned[source_name] = df

            print(
                f"Cleaned {source_name}: "
                f"{df.shape[0]} rows, {df.shape[1]} columns"
            )

        return cleaned

    def normalize(self, cleaned_records: Any) -> Any:
        """
        Apply z-score normalization to numeric features.

        Timestamp, StartTime and Label are kept unchanged.
        """

        normalized = {}

        for source_name, df in cleaned_records.items():

            df = df.copy()

            numeric_columns = df.select_dtypes(
                include=[np.number]
            ).columns.tolist()

            for column in numeric_columns:

                mean = df[column].mean()
                std = df[column].std()

                if pd.isna(std) or std == 0:
                    df[column] = 0.0
                else:
                    df[column] = (
                        (df[column] - mean) / std
                    )

            normalized[source_name] = df

            print(
                f"Normalized {source_name}: "
                f"{len(numeric_columns)} numeric columns"
            )

        return normalized

    def window(self, normalized_records: Any) -> Any:
        """
        Create fixed-size time windows.

        window_size and stride are read from configuration.
        """

        window_size = int(
            self.config.get("window_size", 60)
        )

        stride = int(
            self.config.get("stride", 10)
        )

        windowed = {}

        for source_name, df in normalized_records.items():

            df = df.copy()

            if "Timestamp" not in df.columns:
                raise ValueError(
                    "Timestamp column is required for windowing."
                )

            start_time = df["Timestamp"].min()

            elapsed_seconds = (
                df["Timestamp"] - start_time
            ).dt.total_seconds()

            # Assign each record to a time window
            df["window_id"] = (
                elapsed_seconds // stride
            ).astype(int)

            # Keep only records inside the configured window
            df["window_start"] = (
                start_time
                + pd.to_timedelta(
                    df["window_id"] * stride,
                    unit="s"
                )
            )

            windowed[source_name] = df

            print(
                f"Windowed {source_name}: "
                f"{df['window_id'].nunique()} windows"
            )

        return windowed

    def fuse_sources(self, windowed_records: Any) -> pd.DataFrame:
        """
        Merge all sources into one feature table.

        CIC-IDS-2018 flow files do not always contain an entity ID,
        so a network-level entity is used when no entity column exists.
        """

        frames = []

        for source_name, df in windowed_records.items():

            df = df.copy()

            if "entity_id" not in df.columns:

                if "Src IP" in df.columns:
                    df["entity_id"] = df["Src IP"].astype(str)

                elif "Source IP" in df.columns:
                    df["entity_id"] = df["Source IP"].astype(str)

                else:
                    df["entity_id"] = source_name

            frames.append(df)

        if not frames:
            raise ValueError("No records available for fusion.")

        fused = pd.concat(
            frames,
            ignore_index=True
        )

        return fused

    def run(
        self,
        raw_dir: Path,
        output_path: Path
    ) -> Path:
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
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        fused.to_parquet(
            output_path,
            index=False
        )

        print("\n=== Pipeline Complete ===")
        print(f"Output: {output_path}")
        print(f"Shape: {fused.shape}")

        return output_path