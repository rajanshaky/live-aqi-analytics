from data_pipeline import fetch_data
from db_config import load_to_mysql

if __name__ == "__main__":
    df = fetch_data()
    print(df.head())

    load_to_mysql(df)
