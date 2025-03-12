# final-year-system-e-auction

<!-- ngrok http --domain=tops-cardinal-horribly.ngrok-free.app 8000 // -->
celery -A core beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
celery -A core worker --scheduler django --loglevel=info

########  To start redis in Ubuntu
sudo service redis-server start
redis-cli

Payment
WRONG OTP: 5548
INSUFFICIENT FUNDS: 6648

varid card
Card number: 5531886652142950
cvv: 564
pin 3310
exirty 09/32
otp 12345

Card Insufficient Funds	5258585922666506	883	3310	09/31	12345


varid otp for mobile  OTP 123456.

