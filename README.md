# twilio-ivr

1. This is a simple django based web application which will allow users to create an interactive voice system using twilio.  
2. download and run the `automate.sh` file to finish setting up the server or you can perform the steps manually.
```shell 
wget https://github.com/dhruvarora561/twilio-ivr/blob/main/automate.sh
bash automate.sh
```
To get started, simply clone this repository
```shell
git clone https://github.com/dhruvarora561/twilio-ivr.git
```

Then, create a virtual environment
```shell
python -m venv venv
```
Now, activate it by using
```shell
venv\Scripts\activate
```
Now, we'll need to install some dependencies. We can do that by using
```shell
pip install -r requirements.txt
```
We also need to run migrations
```shell
python ivr/manage.py migrate
```
Lastly, run the server using 
```shell
TWILIO_AUTH_TOKEN=my-twilio-secret-token ivr/manage.py runserver
```
You need a twilio account and a secret auth key to run this system.
