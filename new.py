import os
import stripe
import json
from flask import Flask, jsonify, request
from dhooks import Webhook, Embed

# Add stripe api key here (Use testing key until pushing live.)
stripe.api_key = ''

app = Flask(__name__)

# Send notif
def sendNotification(notification):
    hook = Webhook('Insert webhook here')
    # Set embed info
    embed = Embed(description=notification['description'],timestamp='now',color=notification['color'])
    embed.set_footer(text='Stripe for Discord by mdb5672',
                        icon_url='https://avatars1.githubusercontent.com/u/51242885?s=60&v=4')
    embed.set_author(name='Stripe',
        icon_url='https://pbs.twimg.com/profile_images/1280236709825835008/HmeYTwai_400x400.png')
    for fields in notification['fields']:
        embed.add_field(name=fields['name'],value=fields['value'])
    hook.send(embed=embed)

@app.route('/', methods='POST')

# Stripe events to monitor:
    # charge.succeeded
    # charge.failed
    # charge.refunded
    # customer.subscription.updated
    # invoice.marked_uncollectible

# Handle incoming payload
def parse():
    event = None
    payload = request.data

    try:
        event = json.loads(payload)
    except ValueError as e:
        print('⚠️  Webhook error while parsing basic request.' + str(e))
        return jsonify(success=True)
    except stripe.error.SignatureVerificationError as e:
        print('⚠️  Webhook error while parsing basic request.' + str(e))
        return jsonify(success=True)

    # Handle the event
    notification = []

    if event.type == 'charge.succeeded':
        paymentData = event['data']['object']
        notification['description'] = 'Payment Successful!'
        notification['fields'].append({'name': 'Customer', 'value': paymentData['billing_details']['name']})
        notification['fields'].append({'name': 'Email:', 'value': paymentData['billing_details']['email']})
        notification['fields'].append({'name': 'Amount:', 'value': paymentData['currency'] (paymentData['amount']/100)})
        


