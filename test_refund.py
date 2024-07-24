import stripe

stripe.api_key = 'sk_test_51PbqQGD93W15USiaMasDyqPJtIs1UpgSuLVdPhvxmZ8bYf06KiOils2Qeypque0ZZpjMHqzeQ1LMzHg0ADzjDKby00qL3TIkqb'

def get_payment_id_from_product_id(product_id):
    try:
        # Rechercher les abonnements liés au produit, triés par date de création descendante
        subscriptions = stripe.Subscription.list(
            limit=1,
            status='all',
            expand=['data.latest_invoice']
        )

        for subscription in subscriptions.auto_paging_iter():
            for item in subscription['items']['data']:
                if item['price']['product'] == product_id:
                    latest_invoice = subscription['latest_invoice']
                    if latest_invoice:
                        invoice = stripe.Invoice.retrieve(latest_invoice.id)
                        payment_id = invoice['charge']
                        return payment_id, subscription.id
        return None, None
    except stripe.error.StripeError as e:
        print(f"Une erreur est survenue: {e}")
        return None, None

def desactiver_abonnement(subscription_id):
    try:
        # Désactiver l'abonnement
        stripe.Subscription.delete(subscription_id)
        return f"Abonnement {subscription_id} désactivé avec succès."
    except Exception as e:
        return f"Erreur lors de la désactivation de l'abonnement : {str(e)}"

# Exemple d'utilisation
product_id = 'prod_QX5nfbuHAS8bhT'
refund_amount =  'sz'
if product_id:
    payment_id, subscription_id = get_payment_id_from_product_id(product_id)
    if payment_id and subscription_id:
        try:
            refund = stripe.Refund.create(charge=payment_id, amount=refund_amount)  # Exemple de montant à rembourser
            print(f"Remboursement créé: {refund}")
            desactivation_message = desactiver_abonnement(subscription_id)
            print(desactivation_message)
        except stripe.error.StripeError as e:
            print(f"Erreur lors de la création du remboursement: {e}")



