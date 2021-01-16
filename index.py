import os
import stripe
import json
from flask import Flask, jsonify, request
from dhooks import Webhook, Embed

# Add stripe api key here (Use testing key until pushing live.)
stripe.api_key = ''
# Add stripe secret key here
endpoint_secret = ''

app = Flask(__name__)

# Send notif
def sendNotification(notification):
    hook = Webhook('')
    # Set embed info
    embed = Embed(description=notification['description'],timestamp='now',color=notification['color'])
    embed.set_footer(text='Stripe for Discord by mdb5672',
                        icon_url='https://avatars1.githubusercontent.com/u/51242885?s=60&v=4')
    for fields in notification['fields']:
        embed.add_field(name=str(fields['name']),value=str(fields['value']),inline=False)
    hook.send(embed=embed)

#set listener url
@app.route('/', methods=['POST'])

# Stripe events to monitor:
    # charge.succeeded
    # charge.failed
    # charge.refunded
    # invoice.paid
    # customer.subscription.created
    # customer.subscription.deleted
    # customer.subscription.updated
    # customer.subscription.trail_will_end
    # charge.dispute.created
    # charge.dispute.closed
    # payout.paid
    # payout.failed

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
    
    if endpoint_secret:
        # Only verify the event if there is an endpoint secret defined
        # Otherwise use the basic event deserialized with json
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            print('⚠️  Webhook signature verification failed.' + str(e))
            return jsonify(success=True)

    # Handle the event
    notification = {}
    notification['fields'] = []
    notification['color'] = []
    notification['description'] = []

    if event['type'] == 'charge.succeeded':
        paymentData = event['data']['object']
        notification['description'] = 'Payment Successful'
        notification['fields'].append({'name': 'Customer:', 'value': paymentData['billing_details']['name']})
        notification['fields'].append({'name': 'Email:', 'value': paymentData['billing_details']['email']})
        notification['fields'].append({'name': 'Customer ID:', 'value': paymentData['customer']})
        notification['fields'].append({'name': 'Amount:', 'value': paymentData['currency'] + ' ' + str(paymentData['amount']/100)})
        notification['color'] = '130817'
        sendNotification(notification)

    elif event['type'] == 'charge.failed':
        paymentData = event['data']['object']
        notification['description'] = 'Payment Failed'
        notification['fields'].append({'name': 'Customer:', 'value': paymentData['billing_details']['name']})
        notification['fields'].append({'name': 'Email:', 'value': paymentData['billing_details']['email']})
        notification['fields'].append({'name': 'Customer ID:', 'value': paymentData['customer']})
        notification['fields'].append({'name': 'Amount:', 'value': paymentData['currency'] + ' ' + str(paymentData['amount']/100)})
        notification['color'] = '16711680'
        sendNotification(notification)

    elif event['type'] == 'charge.refunded':
        paymentData = event['data']['object']
        notification['description'] = 'Payment refunded'
        notification['fields'].append({'name': 'Customer:', 'value': paymentData['billing_details']['name']})
        notification['fields'].append({'name': 'Email:', 'value': paymentData['billing_details']['email']})
        notification['fields'].append({'name': 'Customer ID:', 'value': paymentData['customer']})
        notification['fields'].append({'name': 'Amount Refunded:', 'value': paymentData['currency'] + ' ' + str(paymentData['amount_refunded']/100)})
        notification['color'] = '16711680'
        sendNotification(notification)

    elif event['type'] == 'invoice.paid':
        paymentData = event['data']['object']
        notification['description'] = 'Invoice Paid'
        notification['fields'].append({'name': 'Customer:', 'value': paymentData['customer_name']})
        notification['fields'].append({'name': 'Email:', 'value': paymentData['customer_email']})
        notification['fields'].append({'name': 'Amount Due:', 'value': paymentData['amount_due']/100})
        notification['color'] = '130817'
        sendNotification(notification)
    
    elif event['type'] == 'customer.subscription.created':
        paymentData = event['data']['object']
        notification['description'] = 'New Subscription'
        notification['fields'].append({'name': 'Customer ID:', 'value': paymentData['customer']})
        notification['fields'].append({'name': 'Subscription Tier:', 'value': paymentData['items']['data']['price']['nickname']})
        notification['fields'].append({'name': 'Price:', 'value': paymentData['currency'] + ' ' + str(paymentData['items']['data']['price']['unit_amount']/100)})
        notification['fields'].append({'name': 'Discount:', 'value': paymentData['discount']})
        notification['color'] = '130817'
        sendNotification(notification)

    elif event['type'] == 'customer.subscription.deleted':
        paymentData = event['data']['object']
        notification['description'] = 'Subscription Canceled'
        notification['fields'].append({'name': 'Customer ID:', 'value': paymentData['customer']})
        notification['fields'].append({'name': 'Subscription Tier:', 'value': paymentData['items']['data']['price']['nickname']})
        notification['color'] = '16711680'
        sendNotification(notification)
    
    elif event['type'] == 'customer.subscription.updated':
        paymentData = event['data']['object']
        notification['description'] = 'Subscription Updated'
        notification['fields'].append({'name': 'Customer ID:', 'value': paymentData['customer']})
        notification['fields'].append({'name': 'Subscription Tier:', 'value': paymentData['items']['data']['price']['nickname']})
        notification['fields'].append({'name': 'Price:', 'value': paymentData['currency'] + ' ' + str(paymentData['items']['data']['price']['unit_amount']/100)})
        notification['fields'].append({'name': 'Discount:', 'value': paymentData['discount']})
        notification['color'] = '9896172'
        sendNotification(notification)

    elif event['type'] == 'customer.subscription.trial_will_end':
        paymentData = event['data']['object']
        notification['description'] = 'Trial Ending'
        notification['fields'].append({'name': 'Customer ID:', 'value': paymentData['customer']})
        notification['fields'].append({'name': 'Subscription Tier:', 'value': paymentData['items']['data']['price']['nickname']})
        notification['fields'].append({'name': 'Trial End Date:', 'value': paymentData['trial_end']})
        notification['fields'].append({'name': 'Price:', 'value': paymentData['currency'] + ' ' + str(paymentData['items']['data']['price']['unit_amount']/100)})
        notification['fields'].append({'name': 'Discount:', 'value': paymentData['discount']})
        notification['color'] = '9896172'
        sendNotification(notification)

    elif event['type'] == 'charge.dispute.created':
        paymentData = event['data']['object']
        notification['description'] = 'Charge Disputed'
        notification['fields'].append({'name': 'Charge ID:', 'value': paymentData['charge']})
        notification['fields'].append({'name': 'Reason:', 'value': paymentData['reason']})
        notification['fields'].append({'name': 'Status:', 'value': paymentData['status']})
        notification['fields'].append({'name': 'Amount:', 'value': paymentData['currency'] + ' ' + str(paymentData['amount']/100)})
        notification['color'] = '16711680'
        sendNotification(notification)
    
    elif event['type'] == 'charge.dispute.closed':
        paymentData = event['data']['object']
        notification['description'] = 'Dispute Closed'
        notification['fields'].append({'name': 'Charge ID:', 'value': paymentData['charge']})
        notification['fields'].append({'name': 'Reason:', 'value': paymentData['reason']})
        notification['fields'].append({'name': 'Status:', 'value': paymentData['status']})
        notification['fields'].append({'name': 'Amount:', 'value': paymentData['currency'] + ' ' + str(paymentData['amount']/100)})
        notification['color'] = '16607746'
        sendNotification(notification)
    
    elif event['type'] == 'payout.paid':
        paymentData = event['data']['object']
        notification['description'] = 'Payout Sent'
        notification['fields'].append({'name': 'Payout ID:', 'value': paymentData['id']})
        notification['fields'].append({'name': 'Status:', 'value': paymentData['status']})
        notification['fields'].append({'name': 'Amount:', 'value': paymentData['amount']})
        notification['color'] = '130817'
        sendNotification(notification)
    
    elif event['type'] == 'payout.failed':
        paymentData = event['data']['object']
        notification['description'] = 'Payout Failed'
        notification['fields'].append({'name': 'Payout ID:', 'value': paymentData['id']})
        notification['fields'].append({'name': 'Status:', 'value': paymentData['status']})
        notification['fields'].append({'name': 'Amount:', 'value': paymentData['amount']})
        notification['color'] = '16607746'
        sendNotification(notification)

    return jsonify(success=True)


if __name__ == '__main__':
    app.run()