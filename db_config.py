import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE'),
        use_pure=True
    )

def load_to_mysql(df):

    try:

        conn = connect_db()
        cursor = conn.cursor()

        print(f"Rows inserted: {len(df)}")

        query = """
        INSERT INTO aqi_data (
            city, aqi, pm25, pm10, o3, no2, so2, co, timestamp
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for _, row in df.iterrows():

            cursor.execute(query, (
                row['city'],
                row['aqi'],
                row['pm25'],
                row['pm10'],
                row['o3'],
                row['no2'],
                row['so2'],
                row['co'],
                row['timestamp']
            ))

        conn.commit()

        print("Data inserted successfully!")

    except Exception as e:

        print("Database Error:", e)

    finally:

        if conn.is_connected():
            cursor.close()
            conn.close()