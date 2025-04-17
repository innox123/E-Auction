# final-year-system-e-auction

<!-- ngrok http --domain=tops-cardinal-horribly.ngrok-free.app 8000 // -->
celery -A core beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
celery -A core worker --scheduler django --loglevel=info

########  To start redis in Ubuntu
sudo service redis-server start
redis-cli
