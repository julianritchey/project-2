# Library Imports #######################################################################

from flask import Flask, render_template, request
import boto3
import os
from datetime import date
from flask_mail import Mail, Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pathlib
import base64



import botocore.session
from botocore.config import Config

from dotenv import load_dotenv

#######################################################################










# LEX Configurations ###########################################################################


# Load the environment variables from .env file
load_dotenv()

# Create a Flask application
app = Flask(__name__)

# Access the environment variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
My_email = os.getenv('My_email')
Email_Password = os.getenv('Email_Password')


# Configure the AWS region
app.config['AWS_REGION'] = 'us-east-1'  

# Create a Botocore session with the AWS region
session = botocore.session.Session()

# Configure the AWS region in the session
session.set_config_variable('region', app.config['AWS_REGION'])

# Create a client for the Lex bot service using the session
config = Config(region_name=app.config['AWS_REGION'])
lex_client = session.create_client('lex-runtime', config=config)


#######################################################################









#Gmail Setting #######################################################################


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = My_email
app.config['MAIL_PASSWORD'] = Email_Password

mail = Mail(app)

#######################################################################







# Global Variables: #######################################################################
firstName = 'Bob'
dateOfBirth = date.today()
kids = 0
networth = 0
income = 0
marriage = 'yes'



#######################################################################









#Routes ###############################################################

@app.route('/')
def chat():

    return render_template('chat.html')



#Chat Bot
@app.route('/chat', methods=['POST'])
def chat_post():

    global firstName, dateOfBirth, kids, networth, income, marriage

    user_input = request.form['user_input']

    # Generate a unique user ID
    user_id = "test"

    networth = 20

    # Send user input to the bot and receive the response
    response = lex_client.post_text(
        botName= 'RiskScore',
        botAlias= '$LATEST',
        userId= user_id,
        inputText= user_input
    )

    # Extract slot values from the Lex response
    slots = response['slots']
    firstName = slots.get('firstName') 
    dateOfBirth = slots.get('dateOfBirth')
    kids = slots.get('kids')
    networth = slots.get('networth')
    income = slots.get('income')
    marriage = slots.get('marriage')


    # Extract the bot's response from the API response
    bot_response = response['message']

    return bot_response

@app.route ("/test", methods = ["POST", "GET"])
def test():
    global recipient, subject, message 

    return render_template ('test.html', firstName=firstName, dateOfBirth=dateOfBirth, kids=kids, networth=networth, income=income, marriage=marriage)



# Sending Email

@app.route('/send-email', methods=['GET', 'POST'])
def send_email():

    text = 'I am sending this test email'
    msg = Message('Hello from Flask',
                  sender= My_email,
                  recipients=[My_email])
    msg.body = text
    mail.send(msg)
    return 'Email sent successfully!'


#########################################################################################################



if __name__ == '__main__':
    app.run(debug=True)

