from flask import Flask, render_template, request
import uuid
import boto3
import os

import botocore.session
from botocore.config import Config

from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()

# Create a Flask application
app = Flask(__name__)

# Access the environment variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')


# Configure the AWS region
app.config['AWS_REGION'] = 'us-east-1'  # Replace with your desired region

# Create a Botocore session with the AWS region
session = botocore.session.Session()

# Configure the AWS region in the session
session.set_config_variable('region', app.config['AWS_REGION'])

# Create a client for the Lex bot service using the session
config = Config(region_name=app.config['AWS_REGION'])
lex_client = session.create_client('lex-runtime', config=config)


@app.route('/')
def chat():
    #return "Hello World!"
    return render_template('chat.html')


@app.route('/chat', methods=['POST'])
def chat_post():
    user_input = request.form['user_input']

    # Generate a unique user ID
    user_id = "test"

    # Send user input to the bot and receive the response
    response = lex_client.post_text(
        botName= 'RiskScore',
        botAlias= '$LATEST',
        userId= user_id,
        inputText= user_input
    )

    if request.method == 'POST':
        lex_response = request.get_json()

        # Extract slot values from the Lex response
        slots = lex_response['slots']
        firstName = slots.get('firstName') 
        dateOfBirth = slots.get('dateOfBirth')
        kids = slots.get('kids')
        networth = slots.get('networth')
        income = slots.get('income')
        marriage = slots.get('marriage')


    # Extract the bot's response from the API response
    bot_response = response['message']

    return bot_response


if __name__ == '__main__':
    app.run(debug = True)

