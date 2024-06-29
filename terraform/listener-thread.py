import psycopg2
import threading
import time
import subprocess

print("start listener.py")

# Info pour l'auth de la bdd
db_config = {
    'user': 'userHash2ash',
    'password': 'C5yAn39f8Tm7U13z',
    'host': 'db-hash2ash-prod.c3m2i44y2jm0.us-east-1.rds.amazonaws.com',
    'port': '5432',
    'dbname': 'hash2ash'
}

conn = psycopg2.connect(**db_config)
cursor = conn.cursor()

# Constantes pour les états
terminate = "Terminate"
cracked = "Cracked"
notfound = "NotFound"
processing = "Processing"
inqueue = "In Queue"

# Fonction pour lancer une nouvelle instance dans un thread
def launch_newinstance():
    cursor.execute(f"SELECT id_hash FROM public.hashes WHERE status='{inqueue}';")
    results = cursor.fetchall()
    if results:
        for result in results:
            id_hash = result[0]
            subprocess.run(f"./terraform_new_instance.sh {id_hash}", shell=True)
            print(f"Launch instance for id_hash: {id_hash}.")

# Fonction pour terminer une instance dans un thread
def instance_terminate():
    cursor.execute(f"SELECT id_arch FROM public.instances LEFT JOIN public.hashes ON public.hashes.fk_id_instance=public.instances.id_instance WHERE public.hashes.result IS NOT NULL AND public.instances.status != '{terminate}';")
    results = cursor.fetchall()
    if results:
        for result in results:
            id_arch = result[0]
            subprocess.run(f"./instance-status.sh {id_arch} '{terminate}'", shell=True)
            subprocess.run(f"./terraform_stop_instance.sh {id_arch}", shell=True)
            print(f"Instance {terminate}: {id_arch}.")

# Fonction pour gérer les hash crackés dans un thread
def hash_cracked():
    cursor.execute(f"SELECT id_arch FROM public.instances LEFT JOIN public.hashes ON public.hashes.fk_id_instance=public.instances.id_instance WHERE public.hashes.result IS NOT NULL AND public.hashes.status != '{cracked}';")
    results = cursor.fetchall()
    if results:
        for result in results:
            id_arch = result[0]
            subprocess.run(f"./hash-status.sh {id_arch} '{cracked}'", shell=True)
            print(f"Hash {cracked}: from instance {id_arch}.")

# Fonction pour gérer les hash non trouvés dans un thread
def hash_notfound():
    cursor.execute(f"SELECT id_arch FROM public.instances LEFT JOIN public.hashes ON public.hashes.fk_id_instance=public.instances.id_instance WHERE public.hashes.result IS NULL AND public.hashes.status = '{notfound}' AND public.instances.status != '{terminate}';")
    results = cursor.fetchall()
    if results:
        for result in results:
            id_arch = result[0]
            subprocess.run(f"./instance-status.sh {id_arch} '{terminate}'", shell=True)
            subprocess.run(f"./terraform_stop_instance.sh {id_arch}", shell=True)
            print(f"Instance {terminate}: {id_arch} hash not found.")

# Fonction pour gérer les hash en traitement dans un thread
def hash_processing():
    cursor.execute(f"SELECT id_arch FROM public.instances LEFT JOIN public.hashes ON public.hashes.fk_id_instance=public.instances.id_instance WHERE public.hashes.result IS NULL AND public.instances.status = '{processing}' AND public.hashes.status != '{processing}' AND public.hashes.status != '{notfound}';")
    results = cursor.fetchall()
    if results:
        for result in results:
            id_arch = result[0]
            subprocess.run(f"./hash-status.sh {id_arch} '{processing}'", shell=True)
            print(f"Hash {processing}: from instance {id_arch}.")

# Fonction principale pour exécuter toutes les tâches en parallèle
def run_tasks_parallel():
    threads = []

    # Créer et démarrer les threads pour chaque fonction
    threads.append(threading.Thread(target=launch_newinstance))
    threads.append(threading.Thread(target=instance_terminate))
    threads.append(threading.Thread(target=hash_cracked))
    threads.append(threading.Thread(target=hash_notfound))
    threads.append(threading.Thread(target=hash_processing))

    for thread in threads:
        thread.start()

    # Attendre que tous les threads se terminent
    for thread in threads:
        thread.join()

# Boucle pour vérifier les mises à jour de la base de données
try:
    while True:
        run_tasks_parallel()
        time.sleep(1)
except KeyboardInterrupt:
    print("Listener stopped.")
finally:
    cursor.close()
    conn.close()
