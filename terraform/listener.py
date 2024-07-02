import asyncio
import concurrent.futures
import subprocess
import psycopg2
import time

# pip install psycopg2-binary -> required 

print("start listener.py")

# Info pour l'auth de la bdd
db_config = {
    'user': 'userHash2ash',
    'password': 'C5yAn39f8Tm7U13z',
    'host': 'db-hash2ash-prod.c3m2i44y2jm0.us-east-1.rds.amazonaws.com',
    'port': '5432',
    'dbname': 'hash2ash'
}

# Constantes pour les états
terminate   = "Terminate"
cracked     = "Cracked"
notfound    = "NotFound"
processing  = "Processing"
inqueue     = "In Queue"

def get_db_connection():
    return psycopg2.connect(**db_config)

def launch_newinstance():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id_hash FROM public.hashes WHERE status='{inqueue}';")
    results = cursor.fetchall()
    #print(f"results {results}")
    if results:
        for result in results:
            id_hash = result[0]
            # Terraform en cours ? j'attends
            print(f"id_hash: {id_hash} In Queue detected .")
            subprocess.run(f"./terraform_new_instance.sh {id_hash}", shell=True, check=True)
            print(f"Launch instance for id_hash: {id_hash}.")
            time.sleep(60)
    cursor.close()
    conn.close()

def instance_terminate():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id_arch FROM public.instances LEFT JOIN public.hashes ON public.hashes.fk_id_instance=public.instances.id_instance WHERE public.hashes.result IS NOT NULL AND public.instances.status != '{terminate}';")
    results = cursor.fetchall()
    if results:
        for result in results:
            id_arch = result[0]
            subprocess.run(f"./instance-status.sh {id_arch} '{terminate}'", shell=True, check=True)
            subprocess.run(f"./terraform_stop_instance.sh {id_arch}", shell=True, check=True)
            print(f"Instance {terminate}: {id_arch}.")
    cursor.close()
    conn.close()

def hash_cracked():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id_arch FROM public.instances LEFT JOIN public.hashes ON public.hashes.fk_id_instance=public.instances.id_instance WHERE public.hashes.result IS NOT NULL AND public.hashes.status != '{cracked}';")
    results = cursor.fetchall()
    if results:
        for result in results:
            id_arch = result[0]
            subprocess.run(f"./hash-status.sh {id_arch} '{cracked}'", shell=True, check=True)
            print(f"Hash {cracked}: from instance {id_arch}.")
    cursor.close()
    conn.close()

def hash_notfound():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id_arch FROM public.instances LEFT JOIN public.hashes ON public.hashes.fk_id_instance=public.instances.id_instance WHERE public.hashes.result IS NULL AND public.hashes.status = '{notfound}' AND public.instances.status != '{terminate}';")
    results = cursor.fetchall()
    if results:
        for result in results:
            id_arch = result[0]
            subprocess.run(f"./instance-status.sh {id_arch} '{terminate}'", shell=True, check=True)
            subprocess.run(f"./terraform_stop_instance.sh {id_arch}", shell=True, check=True)
            print(f"Instance {terminate}: {id_arch} hash not found.")
    cursor.close()
    conn.close()

def hash_processing():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id_arch FROM public.instances LEFT JOIN public.hashes ON public.hashes.fk_id_instance=public.instances.id_instance WHERE public.hashes.result IS NULL AND public.instances.status = '{processing}' AND public.hashes.status != '{processing}' AND public.hashes.status != '{notfound}';")
    results = cursor.fetchall()
    if results:
        for result in results:
            id_arch = result[0]
            subprocess.run(f"./hash-status.sh {id_arch} '{processing}'", shell=True, check=True)
            print(f"Hash {processing}: from instance {id_arch}.")
    cursor.close()
    conn.close()

async def run_in_executor(func):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, func)

# Fonction principale asynchrone
async def main():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        while True:
            # Créer des tâches asynchrones pour les tâches longues
            asyncio.create_task(run_in_executor(launch_newinstance))
            asyncio.create_task(run_in_executor(instance_terminate))
            asyncio.create_task(run_in_executor(hash_notfound))
            asyncio.create_task(run_in_executor(hash_cracked))
            asyncio.create_task(run_in_executor(hash_processing))

            # Pause asynchrone entre chaque incrémentation pour observer l'effet
            await asyncio.sleep(2)
    except KeyboardInterrupt:
        print("Listener stopped.")
    finally:
        cursor.close()
        conn.close()

# Exécuter la boucle d'événements asyncio
asyncio.run(main())



