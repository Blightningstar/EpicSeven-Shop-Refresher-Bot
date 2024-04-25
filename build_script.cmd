@echo off

REM Run PyInstaller command
call poetry run pyinstaller --log-level=DEBUG ^
    --add-data "e7shop_refresher/image_resources/*;image_resources/" ^
    --add-data ".venv/Lib/site-packages/cv2;cv2" ^
    --add-data ".venv/Lib/site-packages/easyocr;easyocr" ^
    --add-data ".venv/Lib/site-packages/psutil;psutil" ^
    --add-data ".venv/Lib/site-packages/colorama;colorama" ^
    --add-data ".venv/Lib/site-packages/uiautomator2;uiautomator2" ^
    --add-data ".venv/Lib/site-packages/scipy;scipy" ^
    --name e7shop_refresher ^
    e7shop_refresher/main.py
