import re
import uuid

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from ingestion.fastf1_ingestion.ingest import ingestion_session, convert_timedelta_to_ns
from ingestion.fastf1_ingestion.azure_storage import upload_dataset


STORAGE_ACCOUNT = "rgmotorsportdev"

SESSION_NAMES = {
    "R": "race",
    "Q": "qualifying",
    "FP1": "fp1",
    "FP2": "fp2",
    "FP3": "fp3"
}


def upload_session_data(year: int, event: str, session_type: str) -> None:

    run_id = uuid.uuid4().hex

    laps, results, weather = ingestion_session(year, event, session_type)

    laps = convert_timedelta_to_ns(laps).sort_values(["DriverNumber", "LapNumber"])
    results = convert_timedelta_to_ns(results).sort_values("DriverNumber")
    weather = convert_timedelta_to_ns(weather).sort_values("Time")

    event_name = re.sub(r"[^a-z0-9]+", "_", event.lower()).strip("_")
    session_name = SESSION_NAMES.get(session_type.upper(), session_type.lower())

    base_path = f"fastf1/season={year}/event={event_name}/session={session_name}"

    credential = DefaultAzureCredential()

    with BlobServiceClient(
        account_url=f"https://{STORAGE_ACCOUNT}.blob.core.windows.net",
        credential=credential
    ) as blob_service:

        upload_dataset(blob_service, laps, f"{base_path}/laps", run_id)
        upload_dataset(blob_service, results, f"{base_path}/results", run_id)
        upload_dataset(blob_service, weather, f"{base_path}/weather", run_id)


if __name__ == "__main__":
    upload_session_data(2025, "Monaco", "R")