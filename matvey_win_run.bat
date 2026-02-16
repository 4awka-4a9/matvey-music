@echo off
cd /d "%~dp0"
echo 🚀 Proveryayu biblioteki...
pip install -r requirements.txt --quiet
echo ✅ Zapuskayu Matveya...
python main.py
pause