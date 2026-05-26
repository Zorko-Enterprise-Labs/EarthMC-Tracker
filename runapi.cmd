@REM MAKE SURE TO DO pip install gunicorn BEFORE RUNNING SCRIPT
gunicorn api:app --bind 0.0.0.0:5000 --workers 28