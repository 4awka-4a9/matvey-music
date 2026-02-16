#!/bin/bash
cd "$(dirname "$0")"
clear
echo "🚀 Проверяю обновления и библиотеки..."
python3 -m pip install -r requirements.txt --quiet
echo "✅ Всё готово! Запускаю Матвея..."
python3 main.py