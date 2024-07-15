#!/bin/bash
source /tmp/.env_script

if [ $# -ne 2 ]; then
    echo "Usage: $0 <id_arch> <id_hash>"
    exit 1
fi
echo "========================== LANCEMENT DE HASHCAT =========================="

id_arch=$1
id_hash=$2
path_session="/home/ubuntu/.local/share/hashcat/sessions/"
path_zip="/tmp/session_hash2ash.zip"
session_name="session_hash2ash"

status_processing="Processing"

path_result="/tmp/result-$id_arch.txt"
path_parsed_output_hashcat="/tmp/parsed_output_hashcat.txt"
log_hashcat="/tmp/log_hashcat.txt"

path_hash="/tmp/hash.txt"
path_wordlist="/tmp/wordlist.txt"

echo "[VARIABLE INFO - $id_arch] id_arch = $id_arch"
echo "[VARIABLE INFO - $id_arch] id_hash = $id_hash"


# Récuperation de id_instance selon le id_arch 
id_instance=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT id_instance FROM public.instances WHERE id_arch='$id_arch';" | xargs)
echo "[HASHCAT INFO - $id_arch] id_instance = $id_instance"
# Mise à jour de la BDD : fk_id_instance = id_instance
PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.hashes SET fk_id_instance=$id_instance WHERE id_hash='$id_hash';"
## Récuperer les fichiers de session 
url_session_folder=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT session_hashcat FROM public.hashes WHERE id_hash = '$id_hash';" | xargs)
echo "[HASHCAT INFO - $id_arch] url_session_folder = $url_session_folder"
# hashes.status = Processing
echo "[HASHCAT STATUS - $id_arch] Instance $id_arch: $status_processing"
PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.hashes SET status = '$status_processing' WHERE id_hash = $id_hash;"
## Récuperer l'algorithm
algorithm=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT algorithm FROM public.hashes WHERE id_hash='$id_hash';")
echo "[HASHCAT INFO - $id_arch] algorithm = $algorithm"


# Télécharger le fichier de session depuis S3
## Télécharger l'url
echo "[HASHCAT ACTION - $id_arch] Téléchargement du hash en cours : $url_session_folder"
if [ -n "$url_session_folder" ]; then
    echo "[COMMAND - $id_arch] wget \"$session_folder\" -O $path_zip"
    wget "$url_session_folder" -O $path_zip
else
    echo "[HASHCAT ERREUR - $id_arch] URL de la session est introuvable dans la base de données."
    PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE $TABLE_HASHES SET status='Error' WHERE id_hash = $id_hash;"
    exit 1
fi

# Unzip du zip + Déplacement des fichiers aux bons endroits
unzip $path_zip -d $path_session
mv ${path_session}hash.txt /tmp
mv ${path_session}wordlist.txt /tmp
mv ${path_session}hashcat.potfile /home/ubuntu/.local/share/hashcat/

# Lancer Hashcat
echo "[HASHCAT ACTION - $id_arch] hashcat --session="$session_name" --restore | tee -a $log_hashcat | grep -E 'Progress|Estimated|Speed'  > $path_parsed_output_hashcat "
hashcat --session="$session_name" --restore | tee -a $log_hashcat | grep -E "Progress|Estimated|Speed"  > $path_parsed_output_hashcat

hashcat $path_hash $path_wordlist $algorithm --session=session_hash2ash --show
hashcat $path_hash $path_wordlist $algorithm --session=session_hash2ash --show > $path_result


# Envoyer le result en BDD
## Vérifie le code de sortie de hashcat
HASHCAT_EXIT_CODE=$?
line_count=$(wc -l < path_result)
    # 0 = Not found
    # 1 = Cracked

if [ $HASHCAT_EXIT_CODE -ne 0 ] && [ $HASHCAT_EXIT_CODE -ne 1 ]; then
    # probleme au lancement de hashcat
    echo "[HASHCAT ERREUR - $id_arch] Erreur lors du lancement de hashcat avec le code de retour $HASHCAT_EXIT_CODE"
    PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE $TABLE_HASHES SET status='Error' WHERE id_hash = $id_hash;"
elif [ $line_count -eq 0 ]; then
    # password pas trouvé
    echo "[HASHCAT RESULT - $id_arch] Password Exhausted"
    PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE $TABLE_HASHES SET status='Not Found' WHERE id_hash=$id_hash ;"
else
    # Vérifie si Hashcat a été interrompu
    grep "NOTE:" $path_result
    CHECK_KILL=$?
    echo "CHECK_KILL=$CHECK_KILL"

    if [ $CHECK_KILL -eq 0 ]; then
        echo "[HASHCAT STATUS - $id_arch] Hashcat interrompu"

        # Ici vous pouurl_hash_crackedvez ajouter une mise à jour de la BDD si nécessaire
    else
        # Mot de passe trouvé
        echo "[HASHCAT RESULT - $id_arch] Password Cracked"

        # Envoyer le mot de passe en BDD
        while IFS=: read -r hash password; do
            if [ -n "$hash" ] && [ -n "$password" ]; then
                echo "[HASHCAT ACTION - $id_arch] Upload du mot de passe en BDD"

                echo "[COMMAND - $id_arch] aws s3 cp $path_result s3://$BUCKET_NAME_HASH/cracked/result-$id_arch.txt"
                aws s3 cp $path_result s3://$BUCKET_NAME_HASH/cracked/result-$id_arch.txt

                echo "[COMMAND - $id_arch] url_hash_cracked=\"https://$BUCKET_NAME_HASH.s3.amazonaws.com/cracked/result-$id_arch.txt\" "
                url_hash_cracked="https://$BUCKET_NAME_HASH.s3.amazonaws.com/cracked/result-$id_arch.txt"

                PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE $TABLE_HASHES SET result='$url_hash_cracked' WHERE id_hash=$id_hash;"
            fi
        done < $path_result
    fi
fi
