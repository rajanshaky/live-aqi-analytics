import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('OPENAQ_API_KEY')

def fetch_data():

    cities = [
    "Delhi",
    "Mumbai",
    "Bangalore",
    "Hyderabad",
    "Chennai",
    "Kolkata",
    "Lucknow",
    "Kanpur",
    "Patna",
    "Jaipur",
    "Pune",
    "Ahmedabad",
    "Surat",
    "Bhopal",
    "Indore",
    "Varanasi",
    "Nagpur",
    "Vizag",
    "Chandigarh",
    "Gurgaon",
    "Noida",
    "Ghaziabad",
    "Faridabad",
    "Agra",
    "Allahabad",
    "Meerut",
    "Raipur",
    "Ranchi",
    "Sitapur",
    "Amritsar"
]

    records = []

    for city in cities:

        url = f"https://api.waqi.info/feed/{city}/?token={API_KEY}"

        response = requests.get(url)

        data = response.json()

        if data["status"] == "ok":
            iaqi = data["data"].get("iaqi", {})

            records.append({
                "city": city,
                "aqi": data["data"].get("aqi"),
                "pm25": iaqi.get("pm25", {}).get("v"),
                "pm10": iaqi.get("pm10", {}).get("v"),
                "o3": iaqi.get("o3", {}).get("v"),
                "no2": iaqi.get("no2", {}).get("v"),
                "so2": iaqi.get("so2", {}).get("v"),
                "co": iaqi.get("co", {}).get("v"),

                "timestamp": datetime.now()
            })

        else:
            print(f"No data for {city}")
    
    df = pd.DataFrame(records)

    return df