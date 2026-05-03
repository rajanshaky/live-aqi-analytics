"""ETL pipeline for India PM2.5 and PM10 observations from OpenAQ."""

from __future__ import annotations

import logging
import math
import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

import mysql.connector
import requests

from db_config import DB_CONFIG, get_mysql_connection, initialize_database
from env_loader import load_dotenv


load_dotenv()

OPENAQ_BASE_URL = "https://api.openaq.org/v3"
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")
COUNTRY_ISO = os.getenv("OPENAQ_COUNTRY", "IN")
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
PAGE_LIMIT = min(int(os.getenv("OPENAQ_PAGE_LIMIT", "1000")), 1000)
MAX_LOCATION_PAGES = int(os.getenv("OPENAQ_MAX_LOCATION_PAGES", "20"))
MAX_LOCATIONS = int(os.getenv("OPENAQ_MAX_LOCATIONS", "0"))
POLLUTANTS = {"pm25": 2, "pm10": 1}


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if OPENAQ_API_KEY:
        headers["X-API-Key"] = OPENAQ_API_KEY
    return headers


def _request_json(endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Call OpenAQ with retries for transient API failures."""
    url = f"{OPENAQ_BASE_URL}{endpoint}"
    for attempt in range(1, 4):
        try:
            response = requests.get(
                url,
                headers=_headers(),
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            if response.status_code == 429 or 500 <= response.status_code < 600:
                wait_seconds = min(2**attempt, 10)
                logger.warning(
                    "OpenAQ returned %s for %s. Retrying in %ss.",
                    response.status_code,
                    endpoint,
                    wait_seconds,
                )
                time.sleep(wait_seconds)
                continue
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            if attempt == 3:
                raise RuntimeError(f"OpenAQ request failed for {endpoint}: {exc}") from exc
            time.sleep(min(2**attempt, 10))
    return {"results": [], "meta": {"found": 0}}


def _normalize_parameter(raw_parameter: str | None) -> str | None:
    if raw_parameter is None:
        return None
    parameter = raw_parameter.lower().replace(".", "").replace("_", "")
    if parameter in {"pm25", "pm2.5"}:
        return "pm25"
    if parameter == "pm10":
        return "pm10"
    return None


def _parse_utc_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
            timezone.utc
        )
    except ValueError:
        logger.warning("Skipping invalid datetime from API: %s", value)
        return None


def fetch_data() -> list[dict[str, Any]]:
    """Extract latest India PM2.5 and PM10 records from OpenAQ v3."""
    if not OPENAQ_API_KEY:
        raise RuntimeError(
            "OPENAQ_API_KEY is required for OpenAQ API v3. "
            "Set it before running the pipeline."
        )

    locations: dict[int, dict[str, Any]] = {}
    sensor_parameter_map: dict[int, str] = {}
    pollutant_ids = ",".join(str(value) for value in POLLUTANTS.values())

    for page in range(1, MAX_LOCATION_PAGES + 1):
        payload = _request_json(
            "/locations",
            {
                "iso": COUNTRY_ISO,
                "parameters_id": pollutant_ids,
                "limit": PAGE_LIMIT,
                "page": page,
            },
        )
        results = payload.get("results", [])
        if not results:
            break

        for location in results:
            location_id = location.get("id")
            if not location_id:
                continue
            city = location.get("locality") or location.get("name")
            if not city:
                continue
            sensors = location.get("sensors") or []
            supported = set()
            for sensor in sensors:
                parameter = _normalize_parameter(sensor.get("parameter", {}).get("name"))
                sensor_id = sensor.get("id")
                if parameter in POLLUTANTS and sensor_id is not None:
                    supported.add(parameter)
                    sensor_parameter_map[int(sensor_id)] = parameter

            if supported & set(POLLUTANTS):
                locations[int(location_id)] = {"city": city.strip()}

        found = int(payload.get("meta", {}).get("found") or 0)
        if page * PAGE_LIMIT >= found:
            break
        if MAX_LOCATIONS and len(locations) >= MAX_LOCATIONS:
            break

    if MAX_LOCATIONS:
        locations = dict(list(locations.items())[:MAX_LOCATIONS])

    logger.info("Fetched %s India locations with PM sensors.", len(locations))

    records: list[dict[str, Any]] = []
    for location_id, location_meta in locations.items():
        payload = _request_json(f"/locations/{location_id}/latest", {"limit": 100})
        for reading in payload.get("results", []):
            sensor_id = reading.get("sensorsId")
            parameter = sensor_parameter_map.get(int(sensor_id)) if sensor_id else None

            records.append(
                {
                    "city": location_meta["city"],
                    "location_id": location_id,
                    "sensor_id": sensor_id,
                    "parameter": parameter,
                    "value": reading.get("value"),
                    "timestamp": reading.get("datetime", {}).get("utc"),
                }
            )

    logger.info("Fetched %s latest pollutant readings.", len(records))
    return records


def classify_aqi_category(parameter: str, value: float) -> str:
    """Classify particulate concentration into a simple AQI-style category."""
    if parameter == "pm25":
        if value <= 30:
            return "Good"
        if value <= 60:
            return "Moderate"
        if value <= 120:
            return "Poor"
        return "Hazardous"

    if value <= 50:
        return "Good"
    if value <= 100:
        return "Moderate"
    if value <= 250:
        return "Poor"
    return "Hazardous"


def transform_data(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Clean, normalize, and aggregate latest records by city and pollutant."""
    grouped: dict[tuple[str, str], list[tuple[float, datetime]]] = defaultdict(list)

    for record in records:
        city = (record.get("city") or "").strip()
        parameter = _normalize_parameter(record.get("parameter"))
        timestamp = _parse_utc_datetime(record.get("timestamp"))

        try:
            value = float(record.get("value"))
        except (TypeError, ValueError):
            continue

        if not city or parameter not in POLLUTANTS or timestamp is None:
            continue
        if math.isnan(value) or value < 0:
            continue

        grouped[(city, parameter)].append((value, timestamp))

    transformed: list[dict[str, Any]] = []
    for (city, parameter), values in grouped.items():
        avg_value = round(sum(value for value, _ in values) / len(values), 2)
        latest_timestamp = max(timestamp for _, timestamp in values).replace(tzinfo=None)
        transformed.append(
            {
                "city": city[:100],
                "parameter": parameter,
                "value": avg_value,
                "timestamp": latest_timestamp,
                "category": classify_aqi_category(parameter, avg_value),
            }
        )

    transformed.sort(key=lambda row: (row["parameter"], row["value"]), reverse=True)
    logger.info("Transformed %s aggregated city-pollutant records.", len(transformed))
    return transformed


def load_to_mysql(rows: list[dict[str, Any]]) -> int:
    """Load transformed records into MySQL with duplicate protection."""
    if not rows:
        logger.warning("No transformed rows to load.")
        return 0

    initialize_database()
    insert_sql = """
        INSERT IGNORE INTO aqi_data (city, parameter, value, timestamp)
        VALUES (%s, %s, %s, %s)
    """

    inserted = 0
    try:
        with get_mysql_connection(database=DB_CONFIG["database"]) as connection:
            with connection.cursor() as cursor:
                payload = [
                    (row["city"], row["parameter"], row["value"], row["timestamp"])
                    for row in rows
                ]
                cursor.executemany(insert_sql, payload)
                inserted = cursor.rowcount
            connection.commit()
    except mysql.connector.Error as exc:
        raise RuntimeError(f"MySQL load failed: {exc}") from exc

    logger.info("Inserted %s new rows into MySQL.", inserted)
    return inserted


def run_pipeline() -> int:
    """Cron-friendly pipeline entrypoint."""
    raw_records = fetch_data()
    transformed_rows = transform_data(raw_records)
    return load_to_mysql(transformed_rows)


if __name__ == "__main__":
    inserted_count = run_pipeline()
    logger.info("Pipeline completed. New rows inserted: %s", inserted_count)
