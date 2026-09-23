CREATE OR REFRESH STREAMING TABLE motorsport_dev.bronze.results_raw
TBLPROPERTIES (
    'delta.feature.timestampNtz' = 'supported'
)
SELECT
    *,
    _metadata.file_path AS source_file,
    _metadata.file_modification_time AS source_file_modified_at,
    current_timestamp() AS bronze_ingested_at

FROM STREAM read_files(
    '/Volumes/motorsport_dev/bronze/raw_fastf1/fastf1/season=*/event=*/session=*/results/',
    format => 'parquet'
); 