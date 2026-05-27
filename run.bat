@echo off

cd /d "D:\Games\New folder (2)\Projects\live-aqi-analytics"

if not exist logs mkdir logs

echo ============================== >> logs\pipeline_logs.txt
echo Run Time: %date% %time% >> logs\pipeline_logs.txt

.venv\Scripts\python.exe main.py >> logs\pipeline_logs.txt 2>&1

echo. >> logs\pipeline_logs.txt