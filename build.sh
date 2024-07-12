#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install --upgrade pip

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate

# Startup task scheduler
echo "Start task scheduler..."
chmod +x start_task_scheduler.sh
./start_task_scheduler.sh &

# Startup gunicorn
echo "Start gunicorn as WSGI..."
gunicorn --bind 0.0.0.0:5005 core.wsgi:application


