import os
import stripe
import json
from flask import Flask, jsonify, request
from dhooks import Webhook, Embed

# Add stripe api key here (Use testing key until pushing live.)
stripe.api_key = 'pk_test_51HufjkKd0aYbOLmutLvouIrBrKoCUAGmtQUa38yKMuZMSmLwWB3pXLlB6mtiuqrXvvlwdBndaFSEHeRflIMZQmub00LIU9w2Ls'

app = Flask(__name__)

# Send notif
def sendNotification(notification):
    hook = Webhook('https://canary.discord.com/api/webhooks/788922218314203167/YridU4VvmzYzgaJk-7JlLGALSmpnTGtfMLhRe5wqnejW_jYLq5-6QRv8IUm3IQ_CI0fS')
    # Set embed info
    # embed = Embed(description=notification['description'],timestamp='now',color=notification['color'],name='Stripe',avatar='https://pbs.twimg.com/profile_images/1280236709825835008/HmeYTwai_400x400.png')
    embed = Embed()
    embed.set_footer(text='Stripe for Discord by mdb5672',
                        icon_url='https://avatars1.githubusercontent.com/u/51242885?s=60&v=4')
    for fields in notification['fields']:
        embed.add_field(name=fields['name'],value=fields['value'])
    hook.send(embed=embed)

@app.route('/webhook', methods=['POST'])

# Stripe events to monitor:
    # charge.succeeded
    # charge.failed
    # customer.subscription.updated
    # customer.subscription.deleted
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
    notification = {}
    notification['fields'] = []

    if event['type'] == 'charge.succeeded':
        paymentData = event['data']['object']
        notification['description'] = 'Payment Successful!'
        notification['fields'].append({'name': 'Customer', 'value': paymentData['billing_details']['name']})
        notification['fields'].append({'name': 'Email:', 'value': paymentData['billing_details']['email']})
        notification['fields'].append({'name': 'Amount:', 'value': paymentData['currency'] + ' ' + str(paymentData['amount']/100)})
        notification['color'] = '01FF01'
        sendNotification(notification)

    elif event['type'] == 'charge.failed':
        paymentData = event['data']['object']
        notification['description'] = 'Payment Failed.'
        notification['fields'].append({'name': 'Customer', 'value': paymentData['billing_details']['name']})
        notification['fields'].append({'name': 'Email:', 'value': paymentData['billing_details']['email']})
        notification['fields'].append({'name': 'Amount:', 'value': paymentData['currency'] + ' ' + str(paymentData['amount']/100)})
        notification['color'] = 'FF0000'
        sendNotification(notification)
    
    elif event['type'] == 'customer.subscription.updated':
        paymentData = event['data']['object']
        notification['description'] = 'Subscription Updated.'
        notification['fields'].append({'name': 'Customer ID', 'value': paymentData['customer']})
        notification['fields'].append({'name': 'New Tier:', 'value': paymentData['items']['data']['price']['product']})
        notification['color'] = 'FFFF00'
        sendNotification(notification)

    elif event['type'] == 'invoice.marked_uncollectible':
        paymentData = event['data']['object']
        notification['description'] = 'Invoice Unpaid.'
        notification['fields'].append({'name': 'Customer', 'value': paymentData['customer_name']})
        notification['fields'].append({'name': 'Email:', 'value': paymentData['customer_email']})
        notification['fields'].append({'name': 'Amount Due:', 'value': paymentData['amount_due']/100})
        notification['color'] = 'FF0000'
        sendNotification(notification)

    elif event['type'] == 'customer.subscription.deleted':
        paymentData = event['data']['object']
        notification['description'] = 'Invoice Unpaid.'
        notification['fields'].append({'name': 'Customer ID', 'value': paymentData['customer']})
        notification['color'] = 'FF0000'
        sendNotification(notification)

    return jsonify(success=True)


if __name__ == '__main__':
    app.run(port=8080)
