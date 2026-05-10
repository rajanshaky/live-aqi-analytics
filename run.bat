@echo off

cd /d "D:\Games\New folder (2)\Projects\New folder (2)"

call .venv\Scripts\activate

echo ============================== >> logs.txt
echo Run Time: %date% %time% >> logs.txt

python app.py >> logs.txt 2>&1
