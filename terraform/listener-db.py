import asyncio
import concurrent.futures
import subprocess
import psycopg2
import time
from dotenv import load_dotenv
import os


def rouge(text):
    return f"\033[31m{text}\033[0m"

def jaune(text):
    return f"\033[33m{text}\033[0m"

def vert(text):
    return f"\033[32m{text}\033[0m"


load_dotenv()

# pip install psycopg2-binary -> required 

print("start listener.py")

# Info pour l'auth de la bdd

db_config = {
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'dbname': os.getenv('DB_NAME')
}
# Constantes pour les états
terminate   = "Terminate"
cracked     = "Cracked"
notfound    = "Not Found"
processing  = "Processing"
inqueue     = "In Queue"
initialisation =  "Initialisation"
error="Error"

def get_db_connection():
    return psycopg2.connect(**db_config)

def launch_newinstance():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Vérifier s'il y a des statuts 'Initialisation'
    cursor.execute(f"SELECT COUNT(*) FROM public.hashes WHERE status = '{initialisation}';")
    init_count = cursor.fetchone()[0]

    if init_count == 0:
        # Sélectionner le plus petit id_hash avec le statut 'inqueue'
        cursor.execute(f"SELECT id_hash FROM public.hashes WHERE status='{inqueue}' ORDER BY id_hash ASC LIMIT 1;")
        result = cursor.fetchone()
        
        if result:
            id_hash = result[0]
            # Terraform en cours ? j'attends
            print(f"{vert("[ANALYSE BDD]")} id_hash {id_hash} détecté.")
            print(f"{vert("[ACTION]")} Création d'instance pour id_hash : {id_hash}.")
            subprocess.run(f"./terraform_new_instance.sh {id_hash}", shell=True, check=True)
        else:
            print(f"{rouge("[ANALYSE BDD]")} Aucun id_hash en attente.")
    else:
        print(f"{jaune("[ANALYSE BDD]")} Impossible de lancer de nouvelle instance, {init_count} Initialisation d'instance est déjà en cours.")
        print(f"{jaune("[ANALYSE BDD]")} Veuillez patienter...")
        #print(f"[*] id hash {id_hash} en attente")

    cursor.close()
    conn.close()

def instance_terminate():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT id_arch FROM public.instances
        LEFT JOIN public.hashes ON public.hashes.fk_id_instance = public.instances.id_instance
        WHERE (public.hashes.result IS NOT NULL
        AND public.instances.status != '{terminate}')
        OR (public.hashes.status = '{error}'
        AND public.instances.status != '{terminate}');
    """)    
    results = cursor.fetchall()
    if results:
        for result in results:
            id_arch = result[0]
            subprocess.run(f"./instance-status.sh {id_arch} '{terminate}'", shell=True, check=True)
            subprocess.run(f"./terraform_stop_instance.sh {id_arch}", shell=True, check=True)
            print(f"{vert("[STATUS]")} Instance {id_arch} : {terminate}.")
    cursor.close()
    conn.close()

def hash_cracked():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT id_arch FROM public.instances
        LEFT JOIN public.hashes ON public.hashes.fk_id_instance=public.instances.id_instance
        WHERE public.hashes.result IS NOT NULL
        AND public.hashes.status != '{cracked}';
    """)
    results = cursor.fetchall()
    if results:
        for result in results:
            id_arch = result[0]
            subprocess.run(f"./hash-status.sh {id_arch} '{cracked}'", shell=True, check=True)
            print(f"{vert("[STATUS]")} Instance {id_arch} : Hash {cracked}.")
    cursor.close()
    conn.close()

def hash_notfound():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT id_arch FROM public.instances
        LEFT JOIN public.hashes ON public.hashes.fk_id_instance=public.instances.id_instance
        WHERE public.hashes.result IS NULL
        AND public.hashes.status = '{notfound}'
        AND public.hashes.status = '{error}'
        AND public.instances.status != '{terminate}';
    """)
    results = cursor.fetchall()
    if results:
        for result in results:
            id_arch = result[0]
            subprocess.run(f"./instance-status.sh {id_arch} '{terminate}'", shell=True, check=True)
            subprocess.run(f"./terraform_stop_instance.sh {id_arch}", shell=True, check=True)
            print(f"{vert("[STATUS]")} Instance {id_arch} : Hash non trouvé.")
            print(f"{vert("[ACTION]")} Instance {id_arch} : {terminate}.")
    cursor.close()
    conn.close()

def hash_processing():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT id_arch FROM public.instances
        LEFT JOIN public.hashes ON public.hashes.fk_id_instance=public.instances.id_instance
        WHERE public.hashes.result IS NULL
        AND public.instances.status = '{processing}'
        AND public.hashes.status != '{processing}'
        AND public.hashes.status != '{cracked}'
        AND public.hashes.status != '{error}'
        AND public.hashes.status != '{notfound}';
    """)
    results = cursor.fetchall()
    if results:
        for result in results:
            id_arch = result[0]
            subprocess.run(f"./hash-status.sh {id_arch} '{processing}'", shell=True, check=True)
            print(f"{vert("[STATUS]")} Instance {id_arch} : Hash {processing}.")
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
            await asyncio.sleep(5)
    except asyncio.CancelledError:
        print("Fermeture du Listener...")
    except KeyboardInterrupt:
        print("Fermeture du Listener...")
    finally:
        cursor.close()
        conn.close()

# Exécuter la boucle d'événements asyncio
asyncio.run(main())



