@echo off

REM Run PyInstaller command
call poetry run pyinstaller --log-level=DEBUG ^
    --add-data "e7shop_refresher/image_resources/*;image_resources/" ^
    --add-data ".venv/Lib/site-packages/:." ^
    --name e7shop_refresher ^
    e7shop_refresher/main.py
