# India Air Quality Intelligence System

Production-style ETL and dashboard project for India PM2.5 and PM10 data using the OpenAQ API v3, MySQL, and Streamlit.

## Features

- Extracts latest India air-quality readings from OpenAQ API v3.
- Focuses on `pm25` and `pm10`.
- Handles pagination, retries, API errors, null values, invalid values, and duplicate inserts.
- Aggregates average pollutant values per city.
- Loads clean records into MySQL table `aqi_data`.
- Streamlit dashboard with city filter, latest data table, PM2.5 bar chart, AQI category, and most polluted city highlight.

## Project Structure

```text
.
├── app.py
├── data_pipeline.py
├── db_config.py
├── requirements.txt
└── README.md
```

## MySQL Setup

Log in to MySQL and create a user if needed:

```sql
CREATE USER IF NOT EXISTS 'aqi_user'@'localhost' IDENTIFIED BY 'aqi_password';
GRANT ALL PRIVILEGES ON aqi_db.* TO 'aqi_user'@'localhost';
FLUSH PRIVILEGES;
```

The pipeline automatically creates the database and table:

```sql
CREATE DATABASE IF NOT EXISTS aqi_db;

CREATE TABLE IF NOT EXISTS aqi_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100),
    parameter VARCHAR(10),
    value FLOAT,
    timestamp DATETIME
);
```

It also adds a unique key on `(city, parameter, timestamp)` to avoid basic duplicate inserts when OpenAQ returns the same latest measurement again.

## Environment Variables

OpenAQ v3 uses API keys. Register for a key at OpenAQ Explorer and set it before running:

The easiest local setup is to copy `.env.example` to `.env` and fill in your values:

```powershell
Copy-Item .env.example .env
notepad .env
```

At minimum, set:

```text
OPENAQ_API_KEY=your-openaq-api-key
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=aqi_user
MYSQL_PASSWORD=aqi_password
MYSQL_DATABASE=aqi_db
```

Alternatively, set the variables directly in PowerShell:

```powershell
$env:OPENAQ_API_KEY="your-openaq-api-key"
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="aqi_user"
$env:MYSQL_PASSWORD="aqi_password"
$env:MYSQL_DATABASE="aqi_db"
```

Optional tuning:

```powershell
$env:OPENAQ_MAX_LOCATION_PAGES="20"
$env:OPENAQ_MAX_LOCATIONS="0"
$env:OPENAQ_PAGE_LIMIT="1000"
```

Set `OPENAQ_MAX_LOCATIONS` to a small number like `25` while testing.

## Run Locally

Use Python 3.11 or 3.12 for the smoothest Windows install experience. If you are on Python 3.14 and `pandas` tries to compile with Meson or Visual Studio, install Python 3.12 and create the virtual environment with that interpreter.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

If your default `python` points to Python 3.14 on Windows, use the Python launcher explicitly:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

If PowerShell says `No runtime installed that matches 3.12`, install Python 3.12 first:

```powershell
py install 3.12
```

Then close and reopen PowerShell and run the virtual environment commands again.

Run the ETL pipeline:

```powershell
python data_pipeline.py
```

Start the dashboard:

```powershell
python -m streamlit run app.py
```

## Cron-Friendly Usage

The ETL entrypoint is `run_pipeline()` and the script can be scheduled directly:

```bash
0 * * * * cd /path/to/project && /path/to/project/.venv/bin/python data_pipeline.py
```

## Notes

- No web scraping is used. Data comes only from the OpenAQ API.
- OpenAQ reports pollutant concentration values, not official India AQI index values. The dashboard uses a simple category classification for analytics display.
- The dashboard reads from MySQL only; refresh the ETL pipeline to ingest new API data.
