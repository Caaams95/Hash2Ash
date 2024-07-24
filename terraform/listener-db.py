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
error       = "Error"
expired     = "Expired"
stopped     = "Stopped"
want_stop   = "Want Stop"
want_resume = "Want Resume"
resume      = "Resume"
exporting   = "Exporting"

def get_db_connection():
    return psycopg2.connect(**db_config)

def launch_newinstance():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Sélectionner le plus petit id_hash avec le statut 'In Queue'
    cursor.execute(f"SELECT id_hash FROM public.hashes WHERE status='{inqueue}' ORDER BY id_hash ASC LIMIT 1;")
    result = cursor.fetchone()
    
    if result:
        # Vérifier s'il y a des statuts 'Initialisation'
        cursor.execute(f"SELECT COUNT(*) FROM public.hashes WHERE status = '{initialisation}';")
        init_count = cursor.fetchone()[0]
        if init_count == 0:
            id_hash = result[0]
            # Terraform en cours ? terraform_new_instance : j'attends
            print(f"{vert("[ANALYSE BDD]")} id_hash {id_hash} détecté.")
            print(f"{vert("[ACTION]")} Création d'instance pour id_hash : {id_hash}.")
            subprocess.run(f"./terraform_new_instance.sh {id_hash}", shell=True, check=True)
        else:
            print(f"{jaune("[ANALYSE BDD]")} Impossible de lancer de nouvelle instance, {init_count} Initialisation d'instance est déjà en cours.")
            print(f"{jaune("[ANALYSE BDD]")} Veuillez patienter...")
            #print(f"[*] id hash {id_hash} en attente")
    else:
            print(f"{rouge("[ANALYSE BDD]")} Aucun id_hash en attente.")
    
    cursor.close()
    conn.close()

def resume_newinstance():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Sélectionner le plus petit id_hash avec le statut 'In Queue'
    cursor.execute(f"SELECT id_hash FROM public.hashes WHERE status='{want_resume}' ORDER BY id_hash ASC LIMIT 1;")
    result = cursor.fetchone()
    
    if result:
        # Vérifier s'il y a des statuts 'Initialisation'
        cursor.execute(f"SELECT COUNT(*) FROM public.hashes WHERE status = '{initialisation}';")
        init_count = cursor.fetchone()[0]
        if init_count == 0:
            id_hash = result[0]
            # Terraform en cours ? j'attends
            print(f"{vert("[ANALYSE BDD]")} id_hash {id_hash} détecté.")
            print(f"{vert("[ACTION]")} Création d'instance 'Resume' pour id_hash : {id_hash}.")
            subprocess.run(f"./terraform_resume_instance.sh {id_hash}", shell=True, check=True)
        else:
            print(f"{jaune("[ANALYSE BDD]")} Impossible de lancer de nouvelle instance, {init_count} Initialisation d'instance est déjà en cours.")
            print(f"{jaune("[ANALYSE BDD]")} Veuillez patienter...")
            #print(f"[*] id hash {id_hash} en attente")
    else:
            print(f"{rouge("[ANALYSE BDD]")} Aucun id_hash en attente.")

    cursor.close()
    conn.close()


def instance_terminate():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT id_arch FROM public.instances
        LEFT JOIN public.hashes ON public.hashes.fk_id_instance = public.instances.id_instance
        WHERE public.instances.status != '{terminate}'
        AND (public.hashes.result IS NOT NULL
        OR public.hashes.status = '{error}'
        OR public.hashes.status = '{stopped}'
        );
    """)    
    results = cursor.fetchall()
    if results:
        for result in results:
            id_arch = result[0]
            print(f"{vert("[LISTENER ACTION]")} ./instance-status.sh {id_arch} '{terminate}")
            subprocess.run(f"./instance-status.sh {id_arch} '{terminate}'", shell=True, check=True)
            print(f"{vert("[LISTENER ACTION]")} ./terraform_stop_instance.sh {id_arch}")
            subprocess.run(f"./terraform_stop_instance.sh {id_arch}", shell=True, check=True)
            print(f"{vert("[BDD UPDATE]")} ./cost_instance_total.sh {id_arch}")
            subprocess.run(f"./cost_instance_total.sh {id_arch}", shell=True, check=True)           
            print(f"{vert("[STATUS]")} Instance {id_arch} : {terminate}.")
    cursor.close()
    conn.close()


def instance_want_stop():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT id_hash FROM public.hashes
        LEFT JOIN public.instances ON public.instances.id_instance = public.hashes.fk_id_instance
        WHERE public.instances.status != '{terminate}'
        AND public.hashes.status = '{want_stop}'
        ;
    """)    
    results = cursor.fetchall()
    if results:
        for result in results:
            id_hash = result[0]
            print(f"{vert("[LISTENER ACTION]")} ./hash_status.sh {id_hash} {exporting}")
            subprocess.run(f"./hash_status.sh {id_hash} '{exporting}'", shell=True, check=True)
            print(f"{vert("[LISTENER ACTION]")} ./hashcat_stop.sh {id_hash}")
            subprocess.run(f"./hashcat_stop.sh {id_hash}", shell=True, check=True)        
            print(f"{vert("[STATUS]")} Hash {id_hash} : {exporting}.")
    cursor.close()
    conn.close()

def hash_cracked():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT id_hash FROM public.hashes
        WHERE public.hashes.result IS NOT NULL
        AND public.hashes.status != '{cracked}'
        ;
    """)
    results = cursor.fetchall()
    if results:
        for result in results:
            id_hash = result[0]
            subprocess.run(f"./hash_status.sh {id_hash} '{cracked}'", shell=True, check=True)
            print(f"{vert("[STATUS]")} Instance {id_hash} : Hash {cracked}.")
    cursor.close()
    conn.close()

def hash_limit_price():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT id_hash FROM public.hashes
        LEFT JOIN public.instances ON public.instances.id_instance = public.hashes.fk_id_instance
        WHERE public.hashes.price_limit <= public.instances.price_total 
        AND public.hashes.status != '{want_stop}' 
        AND public.hashes.status != '{exporting}' 
        AND public.hashes.status != '{stopped}' 
    ;
    """)    

    results = cursor.fetchall()
    if results:
        for result in results:
            id_hash = result[0]
            subprocess.run(f"./hash_status.sh {id_hash} '{want_stop}'", shell=True, check=True)
            print(f"{vert("[STATUS]")} Instance {id_hash} : Hash {want_stop}.")
    cursor.close()
    conn.close()

def hash_notfound():
    # Hashcat update hashes.status en Not Found automatiquement

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT id_arch FROM public.instances
        LEFT JOIN public.hashes ON public.hashes.fk_id_instance=public.instances.id_instance
        WHERE public.hashes.result IS NULL
        AND public.hashes.status = '{notfound}'
        AND public.instances.status != '{terminate}';
    """)
    
    results = cursor.fetchall()
    if results:
        for result in results:
            id_arch = result[0]
            print(f"{vert("[STATUS]")} Instance {id_arch} : Hash non trouvé.")
            print(f"{vert("[LISTENER ACTION]")} ./instance-status.sh {id_arch} '{terminate}")
            subprocess.run(f"./instance-status.sh {id_arch} '{terminate}'", shell=True, check=True)
            print(f"{vert("[LISTENER ACTION]")} ./terraform_stop_instance.sh {id_arch}")
            subprocess.run(f"./terraform_stop_instance.sh {id_arch}", shell=True, check=True)
            print(f"{vert("[BDD UPDATE]")} ./cost_instance.sh {id_arch}")
            subprocess.run(f"./cost_instance.sh {id_arch}", shell=True, check=True)
            print(f"{vert("[STATUS]")} Instance {id_arch} : {terminate}.")
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
        AND public.hashes.status = '{initialisation}';
    """)
    results = cursor.fetchall()
    if results:
        for result in results:
            id_arch = result[0]
            subprocess.run(f"./hash_status.sh {id_arch} '{processing}'", shell=True, check=True)
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
            asyncio.create_task(run_in_executor(resume_newinstance))
            asyncio.create_task(run_in_executor(instance_terminate))
            asyncio.create_task(run_in_executor(hash_notfound))
            asyncio.create_task(run_in_executor(hash_cracked))
            asyncio.create_task(run_in_executor(hash_limit_price))
            asyncio.create_task(run_in_executor(hash_processing))
            asyncio.create_task(run_in_executor(instance_want_stop))

            # Pause asynchrone entre chaque incrémentation pour observer l'effet
            await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("Fermeture du Listener...")
    except KeyboardInterrupt:
        print("Fermeture du Listener...")
    finally:
        cursor.close()
        conn.close()

# Exécuter la boucle d'événements asyncio
asyncio.run(main())



