import boto3
import json
import psycopg2
from dotenv import load_dotenv
import os
import schedule
import time
import stripe

load_dotenv()
stripe.api_key =  os.getenv('STRIPE_API_KEY')

db_config = {
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'dbname': os.getenv('DB_NAME'),
}

def get_db_connection():
    return psycopg2.connect(**db_config)

def simpleRequestSQL(myrequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""{myrequest}
                   """)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0]


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



def get_refund(id_arch):
    # Récupération du product_id
    product_id=simpleRequestSQL(f"""
                            SELECT id_stripe FROM public.instances
                            WHERE id_arch = '{id_arch}'
                            ;""")

    #    id_arch --> instances.type_instance
    type_instance=simpleRequestSQL(f"""
                            SELECT type_instance FROM public.instances
                            WHERE id_arch = '{id_arch}'
                            ;""")

    
    #    id_arch --> instances.price_total
    price_total=simpleRequestSQL(f"""
                        SELECT price_total FROM public.instances
                        WHERE id_arch = '{id_arch}'
                        ;""")
    
    #    instances.type_instance --> conf_instance.price_has2ash
    price_has2ash=simpleRequestSQL(f"""
                        SELECT price_hash2ash FROM public.conf_instance
                        WHERE type_provider = '{type_instance}'
                        ;""")

    priceDay=price_has2ash*24
    refund_amount = price_total%priceDay
    refund_amount = priceDay - refund_amount
    refund_amount = int(refund_amount * 100)

    # Lancer le remboursement + Stopper l'abonnement
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



def get_ec2_instance_prices(region='us-east-1'):
    session = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
        region_name=region
    )
    client = session.client('pricing', region_name=region)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT type_provider FROM public.conf_instance;
    """)    

    get_instance_types =  cursor.fetchall()
    instance_types = [item[0] for item in get_instance_types]

    instance_prices = []
    for instance_type in instance_types:
        response = client.get_products(
            ServiceCode='AmazonEC2',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
                {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
                {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
                {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'},
                {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'}
            ],
            MaxResults=1
        )
        
        for price_item in response['PriceList']:
            price_item_details = json.loads(price_item)
            for term in price_item_details['terms']['OnDemand'].values():
                for price_dimension in term['priceDimensions'].values():
                    price_per_hour = float(price_dimension['pricePerUnit']['USD'])
                    price_per_day = price_per_hour * 24
                    instance_prices.append({
                        'InstanceType': price_item_details['product']['attributes']['instanceType'],
                        'PricePerHour': price_per_hour,
                        'PricePerDay': price_per_day
                    })
    cursor.close()
    conn.close()  
    return instance_prices


def update_provider_price():
    prices = get_ec2_instance_prices()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for price in prices:
        cursor.execute(f"""
            UPDATE public.conf_instance
            SET price_provider = '{price['PricePerHour']:.2f}'
            WHERE type_provider = '{price['InstanceType']}';
        """)

    conn.commit()
    cursor.close()
    conn.close()

def crontab_24():
    schedule.every(24).hours.do(update_provider_price())

    while True:
        schedule.run_pending()
        time.sleep(1)


