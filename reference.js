// includes
require('dotenv').config();
const app = require('express')();
const bodyParser = require('body-parser');
const Discord = require('discord.js');
const t = require('./tools');

// stripe settings & includes
// Find your endpoint's secret in your Dashboard's webhook settings
const stripe = require('stripe')(process.env.API_KEY);
const endpointSecret = process.env.ENDPOINT_SECRET;

// convert webhook link to id/token pair
const [webhookId, webhookSecret] = process.env.PAYMENT_HOOK.split('/').slice(5);
const hook = new Discord.WebhookClient(webhookId, webhookSecret);

app.get('/', (request, response) => {
    response.status(200).json({
        response: true,
        description: 'Stripe to discord by @darroneggins',
    });
});

// Match the raw body to content type application/json
app.post(
    '/webhook',
    bodyParser.raw({ type: 'application/json' }),
    (request, response) => {
        let event;
        let email;
        let paymentData;

        const sig = request.headers['stripe-signature'];

        try {
            event = stripe.webhooks.constructEvent(
                request.body,
                sig,
                endpointSecret,
            );
        } catch (err) {
            response.status(400).send(`Webhook Error: ${err.message} `);
        }

        const embed = t.makeEmbed();

        // Handle the event
        switch (event.type) {
            case 'charge.succeeded':
                paymentData = event.data.object;

                console.log(paymentData);

                email =
                    paymentData.billing_details.email != null
                        ? paymentData.billing_details.email
                        : paymentData.description;

                embed
                    .setColor('#77dd77')
                    .setThumbnail(t.gravatar(paymentData.description))
                    .setURL(
                        `https://dashboard.stripe.com/payments/${paymentData.id}`,
                    )
                    .addField(
                        `New Payment`,
                        paymentData.billing_details.name,
                        true,
                    )
                    .addField(
                        `Amount`,
                        new Intl.NumberFormat('en-US', {
                            style: 'currency',
                            currency: paymentData.currency,
                        }).format(paymentData.amount / 100),
                        true,
                    )
                    .addField(`Email`, email);

                hook.send(embed);

                return response.status(200).send(paymentData);

            case 'charge.failed':
                paymentData = event.data.object;

                email =
                    paymentData.billing_details.email != null
                        ? paymentData.billing_details.email
                        : paymentData.description;

                embed
                    .setColor('#ff6961')
                    .setThumbnail(t.gravatar(paymentData.description))
                    .setURL(
                        `https://dashboard.stripe.com/payments/${paymentData.id}`,
                    )
                    .addField(
                        `Failed Payment`,
                        paymentData.billing_details.name,
                        true,
                    )
                    .addField(
                        `Amount`,
                        new Intl.NumberFormat('en-US', {
                            style: 'currency',
                            currency: paymentData.currency,
                        }).format(paymentData.amount / 100),
                        true,
                    )
                    .addField(`Email`, email);

                hook.send(embed);

                return response.status(200).send(paymentData);

            case 'transfer.paid':
            case 'payout.paid':
                paymentData = event.data.object;

                embed
                    .setColor('#00bfff')
                    .setThumbnail(t.gravatar(paymentData.description))
                    .setURL(
                        `https://dashboard.stripe.com/payouts/${paymentData.id}`,
                    )
                    .addField(
                        `Payout Paid`,
                        new Intl.NumberFormat('en-US', {
                            style: 'currency',
                            currency: paymentData.currency,
                        }).format(paymentData.amount / 100),
                        true,
                    );

                hook.send(embed);

                return response.status(200).send(paymentData);

            default:
                // Unexpected event type
                return response.status(400).end();
        }
    },
);

const port = process.env.PORT || 5000;

app.listen(port, () => {
    console.log(`Express Server is now running on port ${port} `);
});