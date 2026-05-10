@echo off

echo ============================== >> logs.txt
echo Run Time: %date% %time% >> logs.txt

call .venv\Scripts\activate

python app.py >> logs.txt 2>&1