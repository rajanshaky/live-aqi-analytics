@echo off

cd /d "D:\Games\New folder (2)\Projects\live_aqi_analytics"

call .venv\Scripts\activate

echo ============================== >> logs\pipeline_logs.txt
echo Run Time: %date% %time% >> logs\pipeline_logs.txt

python main.py >> logs\pipeline_logs.txt 2>&1

echo. >> logs\pipeline_logs.txt

