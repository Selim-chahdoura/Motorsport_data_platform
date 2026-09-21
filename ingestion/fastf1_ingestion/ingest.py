import fastf1
import hashlib

import pandas as pd
from pathlib import Path

def ingestion_session(year, event, session_type):
    cache_dir = Path("cache")
    cache_dir.mkdir(exist_ok=True)

    fastf1.Cache.enable_cache(str(cache_dir))

    session = fastf1.get_session(year, event, session_type)
    session.load(telemetry=False, messages=False)

    laps = session.laps
    results = session.results
    weather = session.weather_data

    return laps, results, weather
lap, result, weather = ingestion_session(2023, 'Monaco', 'R')


def convert_timedelta_to_ns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert all Timedelta columns to nullable Int64 nanoseconds
    """
    result = df.copy()

    for column in result.columns:

        if pd.api.types.is_timedelta64_dtype(result[column]):

            converted = result[column].astype("int64").astype("Int64")

            result[column] = converted.mask(result[column].isna())

    return result

def save_to_parquet(df: pd.DataFrame, destination: str | Path) -> None:
    """
    Save a DataFrame as a Parquet file
    """
    destination = Path(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(
        destination,
        engine="pyarrow",
        index=False
    )

def calculate_file_hash(file_path: str | Path) -> str:
    """
    Calculate the SHA-256 hash of a file.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()