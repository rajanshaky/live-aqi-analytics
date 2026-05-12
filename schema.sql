use aqi_db;

DROP TABLE aqi_data;

CREATE TABLE aqi_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100),
    aqi INT,
    pm25 FLOAT,
    pm10 FLOAT,
    o3 FLOAT,
    no2 FLOAT,
    so2 FLOAT,
    co FLOAT,
    timestamp DATETIME
);

select * from aqi_data;