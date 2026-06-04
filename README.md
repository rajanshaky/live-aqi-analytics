# 🌍 Live AQI & Pollutant Analysis Dashboard

[![Live Dashboard](https://img.shields.io/badge/Live-Dashboard-brightgreen)](https://live-aqi-analytics.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![MySQL](https://img.shields.io/badge/MySQL-Railway-orange)](https://railway.app)
[![Streamlit](https://img.shields.io/badge/Streamlit-Deployed-red)](https://streamlit.io)

A real-time Air Quality Index (AQI) monitoring and analytics system built using Python, MySQL, Power BI, and Streamlit.

This project automatically collects air quality data for 25+ major Indian cities, stores it in a cloud MySQL database through an automated ETL pipeline, and visualizes insights through both a Power BI dashboard and a live publicly accessible Streamlit dashboard.

🔗 **Live Dashboard:** [live-aqi-analytics.streamlit.app](https://live-aqi-analytics.streamlit.app)

---

## 📌 Project Overview

The goal of this project is to:

* Monitor live AQI trends across Indian cities
* Analyze pollutant intensity patterns
* Automate data collection and storage
* Build professional analytics dashboards for environmental monitoring
* Demonstrate end-to-end data analytics workflow

The system continuously fetches AQI and pollutant data using the WAQI public API, stores the processed data into a cloud MySQL database on Railway, and visualizes the results through two layers:
- **Power BI** — for rich, interactive BI dashboard development
- **Streamlit + Plotly** — for live public deployment accessible to anyone

---

## ⚙️ Tech Stack

| Category        | Technologies                          |
| --------------- | ------------------------------------- |
| Programming     | Python                                |
| Database        | MySQL (Railway Cloud)                 |
| Data Processing | Pandas                                |
| API Handling    | Requests (WAQI API)                   |
| Visualization   | Power BI, Streamlit, Plotly           |
| Deployment      | Streamlit Cloud + Railway             |
| Automation      | Windows Task Scheduler + Batch Script |
| Environment     | Virtual Environment (.venv)           |

---

## 📂 Project Structure

```bash
live_aqi_analytics/
│
├── .venv/
├── assets/
│   └── monitoring_overview.png
│   └── pattern_exploration.png
│
├── logs/
│   └── pipeline_logs.txt
│
├── .env
├── .env.example
├── .gitignore
│
├── app.py                  ← Streamlit dashboard
├── data_pipeline.py        ← API fetch + transform
├── db_config.py            ← MySQL connection + load
├── main.py                 ← Pipeline entry point
│
├── dashboard.pbix  ← Power BI dashboard file
├── schema.sql
├── requirements.txt
├── run.bat
└── README.md
```

---

## 🔄 ETL Pipeline Workflow

```
WAQI REST API
      ↓
Python (fetch + transform)
      ↓
MySQL on Railway (cloud database)
      ↓
Power BI Dashboard (.pbix)
      +
Streamlit Dashboard (live-aqi-analytics.streamlit.app)
```

### 1. Extract
The Python pipeline fetches live AQI data from the WAQI API for 25+ Indian cities.

Collected metrics:
* AQI, PM2.5, PM10, NO2, O3, SO2, CO, Timestamp

### 2. Transform
The fetched JSON data is cleaned and transformed using Pandas:
* Filtering missing values
* Structuring pollutant columns
* Timestamp formatting
* Creating analytics-ready datasets

### 3. Load
The processed data is inserted into a cloud MySQL database on Railway using `mysql-connector-python`. The pipeline runs automatically through Windows Task Scheduler.

---

## 🗄️ Database Schema

```sql
CREATE TABLE aqi_data (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    city      VARCHAR(100),
    aqi       FLOAT,
    pm25      FLOAT,
    pm10      FLOAT,
    no2       FLOAT,
    o3        FLOAT,
    so2       FLOAT,
    co        FLOAT,
    timestamp DATETIME
);
```

---

## 📊 Power BI Dashboard

The Power BI dashboard (`powerbi_dashboard.pbix`) provides rich interactive visualizations connected directly to the MySQL database.

### Page 1 — Live AQI Monitoring
* Avg AQI, Max AQI, Total Cities, Avg PM2.5 KPI cards
* Top 10 polluted cities horizontal bar chart (color-coded by severity)
* Pollutant comparison grouped bar chart (PM2.5, PM10, NO2)
* AQI trend over time line chart
* Interactive city slicer

### Page 2 — Pollution Pattern Analysis
* AQI severity distribution donut chart (Good / Moderate / Poor / Very Poor / Severe)
* City-wise pollutant intensity heatmap table
* Hourly AQI pattern line chart
* Automated key insights panel
* Last data refresh timestamp

### Dashboard Preview

#### Page 1 — Live AQI Monitoring

![Dashboard 1](assets/monitoring_overview.png)

#### Page 2 — Pollution Pattern Analysis

![Dashboard 2](assets/pattern_exploration.png)

---

## 🌐 Streamlit Live Dashboard

Since Power BI requires a Pro license for public sharing, the dashboard was also rebuilt using **Streamlit + Plotly** and deployed publicly on Streamlit Cloud — connected to the same cloud MySQL database on Railway.

🔗 **[live-aqi-analytics.streamlit.app](https://live-aqi-analytics.streamlit.app)**

### Features
* Identical layout and insights to the Power BI dashboard
* Fully interactive — city filter, hover tooltips, live data
* Publicly accessible — no login required
* Auto-refreshes data every 5 minutes

---

## 🤖 Automation Setup

The pipeline is automated using Windows Task Scheduler + a batch script (`run.bat`):

1. Activates the virtual environment
2. Runs the Python ETL pipeline
3. Logs execution into `pipeline_logs.txt`

---

## ▶️ How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/rajanshaky/live-aqi-analytics.git
cd live-aqi-analytics
```

### 2. Create & Activate Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file:
```env
MYSQL_HOST=your_host
MYSQL_PORT=3306
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
OPENAQ_API_KEY=your_api_key
```

### 5. Run the Pipeline
```bash
python main.py
```

### 6. Launch the Streamlit Dashboard
```bash
streamlit run app.py
```

---

## 🧠 Skills Demonstrated

* Python programming & REST API integration
* ETL pipeline development
* Data transformation with Pandas
* Cloud MySQL database management (Railway)
* Power BI dashboard development
* Interactive dashboard development (Streamlit + Plotly)
* Cloud deployment (Streamlit Cloud)
* Automation scripting
* End-to-end analytics workflow

---

## 👨‍💻 Author

**Rajan Shaky**
Aspiring Data Analyst | Python • SQL • Power BI • Streamlit

[![GitHub](https://img.shields.io/badge/GitHub-rajanshaky-black)](https://github.com/rajanshaky)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com/in/rajanshaky)

---

⭐ If you found this project useful, consider starring the repository!