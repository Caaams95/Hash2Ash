import stripe


def create_checkout_session():
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price.id,  # ID du prix créé
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=url_for('payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('payment_cancel', _external=True),
        )

        # Récupérer l'ID du payment intent
        session = stripe.checkout.Session.retrieve(checkout_session.id, expand=["payment_intent"])
        payment_intent_id = session.payment_intent

        if payment_intent_id:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if payment_intent.charges.data:
                charge_id = payment_intent.charges.data[0].id

                # Effectuer le remboursement automatique
                stripe.Refund.create(
                    charge=charge_id,
                    amount=1000  # Montant en cents pour 10 $
                    print(charge_id)
                )