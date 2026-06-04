import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def connect_local():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user=os.getenv('LOCAL_MYSQL_USER'),
        password=os.getenv('LOCAL_MYSQL_PASSWORD'),
        database=os.getenv('LOCAL_MYSQL_DATABASE'),
        use_pure=True
    )

def connect_railway():
    return mysql.connector.connect(
        host=os.getenv('RAILWAY_MYSQL_HOST'),
        port=int(os.getenv('RAILWAY_MYSQL_PORT', 3306)),
        user=os.getenv('RAILWAY_MYSQL_USER'),
        password=os.getenv('RAILWAY_MYSQL_PASSWORD'),
        database=os.getenv('RAILWAY_MYSQL_DATABASE'),
        use_pure=True
    )

def insert_data(conn, cursor, df):
    query = """
    INSERT INTO aqi_data (
        city, aqi, pm25, pm10, o3, no2, so2, co, timestamp
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    for _, row in df.iterrows():
        cursor.execute(query, (
            row['city'], row['aqi'], row['pm25'], row['pm10'],
            row['o3'], row['no2'], row['so2'], row['co'], row['timestamp']
        ))
    conn.commit()

def load_to_mysql(df):
    for label, connect_fn in [("Local", connect_local), ("Railway", connect_railway)]:
        conn = None
        try:
            conn = connect_fn()
            cursor = conn.cursor()
            insert_data(conn, cursor, df)
            print(f"{label} DB — {len(df)} rows inserted successfully!")
        except Exception as e:
            print(f"{label} DB Error: {e}")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

