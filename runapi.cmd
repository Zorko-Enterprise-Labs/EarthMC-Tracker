@REM gunicorn doesn't run on Windows, so this uses Flask's built-in server instead.
@REM For the map and tile downloader as well, run: python server.py
python api.py
