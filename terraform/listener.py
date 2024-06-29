import psycopg2
import subprocess
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

conn = psycopg2.connect(**db_config)
cursor = conn.cursor()


# Instance
terminate   = "Terminate"
## processing  = "Processing" # Default input by other script
## stop        = "Stop"

# Hash
cracked     = "Cracked"
notfound    = "NotFound"
processing  = "Processing"
inqueue     = "In Queue"

def launch_newinstance():
    # Launch new instance
    cursor.execute(f"SELECT id_hash FROM public.hashes WHERE status='{inqueue}';")
    results=cursor.fetchall()
    if results:
        for result in results:
            id_hash =  result[0]
            subprocess.run(f"./terraform_new_instance.sh {id_hash}", shell=True, check=True)
            print(f"Launch instance for id_hash : {id_hash} .")
    

def instance_terminate():
    # Shutdown instance hash find
    cursor.execute(f"SELECT id_arch FROM public.instances LEFT JOIN public.hashes ON public.hashes.fk_id_instance=public.instances.id_instance WHERE public.hashes.result IS NOT NULL AND public.instances.status != '{terminate}';")
    results=cursor.fetchall()
    if results:
        for result in results:
            id_arch =  result[0]
            subprocess.run(f"./instance-status.sh {id_arch} '{terminate}'", shell=True, check=True)
            subprocess.run(f"./terraform_stop_instance.sh {id_arch}", shell=True, check=True)

            print(f"Instance {terminate} : {id_arch} .")
        
def hash_cracked():
    # Shutdown instance hash find
    cursor.execute(f"SELECT id_arch FROM public.instances LEFT JOIN public.hashes ON public.hashes.fk_id_instance=public.instances.id_instance WHERE public.hashes.result IS NOT NULL AND public.hashes.status != '{cracked}';")
    results=cursor.fetchall()
    if results:
        for result in results:
            id_arch =  result[0]
            subprocess.run(f"./hash-status.sh {id_arch} '{cracked}'", shell=True, check=True)
            print(f"Hash {cracked} : from instance {id_arch} .")
        
def hash_notfound(): # Mixer avec hash_terminate()
    # Shutdown instance hash find
    cursor.execute(f"SELECT id_arch FROM public.instances LEFT JOIN public.hashes ON public.hashes.fk_id_instance=public.instances.id_instance WHERE public.hashes.result IS NULL AND public.hashes.status = '{notfound}' AND public.instances.status != '{terminate}';")
    results=cursor.fetchall()
    if results:
        for result in results:
            id_arch =  result[0]
            subprocess.run(f"./instance-status.sh {id_arch} '{terminate}'", shell=True, check=True)
            subprocess.run(f"./terraform_stop_instance.sh {id_arch}", shell=True, check=True)
            print(f"Instance {terminate} : {id_arch} hash not found .")


def hash_processing():
    # Shutdown instance hash find
    cursor.execute(f"SELECT id_arch FROM public.instances LEFT JOIN public.hashes ON public.hashes.fk_id_instance=public.instances.id_instance WHERE public.hashes.result IS NULL AND public.instances.status = '{processing}' AND public.hashes.status != '{processing}' AND public.hashes.status != '{notfound}' ;")
    results=cursor.fetchall()
    if results:
        for result in results:
            id_arch =  result[0]
            subprocess.run(f"./hash-status.sh {id_arch} '{processing}'", shell=True, check=True)
            print(f"Hash {processing} : from instance {id_arch} .")


# Boucle pour check les update de la bdd
try:
    while True:
        launch_newinstance()
        instance_terminate()
        hash_cracked()
        hash_notfound()
        hash_processing()

        time.sleep(1)
except KeyboardInterrupt:
    print("Listenner stopted.")
finally:
    cursor.close()
    conn.close()