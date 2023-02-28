 #!/bin/bash

echo "This script will setup your twilio-ivr in just a few minutes"


echo "setting up virtual environment"

sudo apt install python3-venv
python3 -m venv venv
echo "activating virtual environment"

source venv/bin/activate

echo "installing dependencies"
pip3 install django
pip3 install twilio

echo "cloning the repository"
git clone https://github.com/dhruvarora561/twilio-ivr.git
cd twilio-ivr

echo "Now you need to enter your twilio auth key"
read authtoken
export TWILIO_AUTH_TOKEN=$authtoken

echo "running database migrations"
python3 ivr/manage.py migrate
echo "staring web server on port 8000"
python3 ivr/manage.py runserver
