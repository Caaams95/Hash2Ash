import boto3
import json
import psycopg2
from dotenv import load_dotenv
import os
import schedule
import time

db_config = {
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'dbname': os.getenv('DB_NAME')
}


def get_db_connection():
    return psycopg2.connect(**db_config)


def get_ec2_instance_prices(region='us-east-1'):

    
    session = boto3.Session(
        os.getenv('AWS_ACCESS_KEY'),
        os.getenv('AWS_SECRET_KEY'),
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


crontab_24()