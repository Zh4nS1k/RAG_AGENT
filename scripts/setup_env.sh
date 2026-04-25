#!/bin/bash
# Скрипт для быстрой настройки окружения
echo "Setting up development environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "Done. Use 'source venv/bin/activate' to start."
