import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="2002",
        database="aqi_db",
        use_pure=True
    )

def load_to_mysql(df):

    try:

        conn = connect_db()
        cursor = conn.cursor()

        print(f"Rows inserted: {len(df)}")

        query = """
        INSERT INTO aqi_data (city, aqi, dominant_pollutant)
        VALUES (%s, %s, %s)
        """

        for _, row in df.iterrows():

            cursor.execute(query, (
                row['city'],
                row['aqi'],
                row['dominant_pollutant']
            ))

        conn.commit()

        print("Data inserted successfully!")

    except Exception as e:

        print("Database Error:", e)

    finally:

        if conn.is_connected():
            cursor.close()
            conn.close()