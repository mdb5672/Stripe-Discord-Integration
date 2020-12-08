import os
import stripe
import json
from flask import Flask, jsonify, request

# Add stripe api key here (Use testing key until pushing live.)
stripe.api_key = ''

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])

# Parse the data
def parse():
    event = None
    payload = request.data

    try:
        event = json.loads(payload)
    except:
        print(f'Error while parsing Webhook: {event}')
    