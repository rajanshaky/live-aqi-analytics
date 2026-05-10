import requests
import pandas as pd
from datetime import datetime

API_KEY = "6bf9d4558a5a9ff8df8fe769ae89ea172d1aee4c"

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

            records.append({
                "city": city,
                "aqi": data["data"]["aqi"],
                "dominant_pollutant": data["data"]["dominentpol"],
                "timestamp": datetime.now()
            })

        else:
            print(f"No data for {city}")
    
    df = pd.DataFrame(records)

    return df