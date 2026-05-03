create database aqi_db;

use aqi_db;

create table aqi_data (
id int auto_increment primary key,
city varchar(20),
parameter varchar(20),
raw_value float,
timestamp datetime);
