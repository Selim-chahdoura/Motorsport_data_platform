import hashlib
from io import BytesIO
from datetime import datetime, timezone

import pandas as pd

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError


STORAGE_ACCOUNT = "rgmotorsportdev"
CONTAINER = "raw"


def serialize_to_parquet(df: pd.DataFrame) -> bytes:
    """Serialize a DataFrame to Parquet in memory."""

    buffer = BytesIO()

    df.to_parquet(buffer, engine="pyarrow", index=False, coerce_timestamps="us")

    return buffer.getvalue()


def calculate_hash(data: bytes) -> str:
    """Calculate SHA-256 from serialized Parquet bytes."""

    return hashlib.sha256(data).hexdigest()


def upload_dataset(blob_service: BlobServiceClient, dataframe: pd.DataFrame, base_path: str, run_id: str) -> bool:
    """
    Upload a dataset only if its content hash does not already exist.

    Returns True if uploaded, False if skipped.
    """
    parquet_bytes = serialize_to_parquet(dataframe)

    content_hash = calculate_hash(parquet_bytes)

    blob_path = f"{base_path}/{content_hash}.parquet"

    blob_client = blob_service.get_blob_client(
        container=CONTAINER,
        blob=blob_path
    )

    if blob_client.exists():
        print(f"SKIPPED: {blob_path}")
        return False

    try:
        blob_client.upload_blob(
            parquet_bytes,
            overwrite=False,
            metadata={
                "source": "fastf1",
                "extracted_at": datetime.now(timezone.utc).isoformat(),
                "ingestion_run_id": run_id
            }
        )

        print(f"UPLOADED: {blob_path}")

        return True

    except ResourceExistsError:
        print(f"SKIPPED (already uploaded): {blob_path}")
        return False