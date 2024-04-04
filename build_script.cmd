@echo off

REM Run PyInstaller command
call poetry run pyinstaller --hidden-import=scipy.special._cdflib ^
    --add-data "e7shop_refresher/image_resources/*;image_resources/" ^
    e7shop_refresher/main.py
