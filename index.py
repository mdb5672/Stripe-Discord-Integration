import os
import stripe
import json
from flask import Flask, jsonify, request
from dhooks import Webhook, Embed

# Add stripe api key here (Use testing key until pushing live.)
stripe.api_key = ''

app = Flask(__name__)

# Send discord webhook
def sendNotification(notification):
    hook = Webhook(notification['webhook'])
    embed = Embed(description=notification['description'], timestamp='now')
    embed.set_title(name=notification['title'])
    embed.set_footer(text=notification['footer'])
    for fields in notification['fields']:
        embed.add_field(name=fields['name'], value=fields['value'])

    embed.set_footer(text=notification['footer'])

    hook.send(embed=embed)

@app.route('/webhook', methods=['POST'])

#Stripe events to monitor:
 # charge.succeeded
 # charge.failed
 # payout.paid


# Parse the data
def parse():
    event = None
    payload = request.data
    notification = {}
    notification['fields'] = []
    notification['webhook'] = ''

    try:
        event = json.loads(payload)
    except:
        print(f'Error while parsing Webhook: {event}')
        return jsonify(success=True)

    # Handle the event
    if event and event['type'] == 'charge.succeeded':
        payment_data = event['data']['object']  # contains a stripe.PaymentIntent
        print('Payment for {} succeeded'.format(payment_data['amount']))

        notification['title'] = 'New Payment'
        notification['description'] = f'https://dashboard.stripe.com/payments/{payment_data['id']}'
        notification['footer'] = 'Stripe to Discord'
        notification['fields'].append({'name':'Email:', 'value':f'{payment_data['billing_details']['email']}'})
        notification['fields'].append({'name':'User:', 'value':f'{payment_data['billing_details']['name']}'})
        notification['fields'].append({'name':'Amount:', 'value':f'{payment_data['currency']} {payment_data['amount']/100}'})
        sendNotification(notification)

    elif event['type'] == 'payment_method.attached':
        payment_data = event['data']['object']  # contains a stripe.PaymentMethod
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)
    else:
        # Unexpected event type
        print(f'Unhandled event type {event["type"]}')

    return jsonify(success=True)
