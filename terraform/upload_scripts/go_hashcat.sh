#!/bin/bash
source /tmp/.env_script

if [ $# -ne 2 ]; then
    echo "Usage: $0 <id_arch> <id_hash>"
    exit 1
fi
echo "========================== LANCEMENT DE HASHCAT =========================="

id_arch=$1
id_hash=$2

status_processing="Processing"

path_hash="/tmp/hash.txt"
path_result="/tmp/result-$id_arch.txt"

temp_wordlist_file="/tmp/wordlist_temp.txt"
final_wordlist_file="/tmp/wordlist.txt"
custom_worldist_file="/tmp/custom_worldist_file.txt"

path_parsed_output_hashcat="/tmp/parsed_output_hashcat.txt"
log_hashcat="/tmp/log_hashcat.txt"


echo "[VARIABLE INFO] id_arch = $id_arch"
echo "[VARIABLE INFO] id_hash = $id_hash"
# Récuperation de id_instance selon le id_arch 
id_instance=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT id_instance FROM public.instances WHERE id_arch='$id_arch';" | xargs)
echo "[HASHCAT INFO] id_instance = $id_instance"
# Mise à jour de la BDD : fk_id_instance = id_instance
PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.hashes SET fk_id_instance=$id_instance WHERE id_hash='$id_hash';"
## Récuperer l'url_hash
url_hash=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT hash FROM public.hashes WHERE id_hash = $id_hash;" | xargs)
echo "[HASHCAT INFO] url_hash = $url_hash"
## Récuperation de la wordlist en BDD
wordlists=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT wordlist FROM public.hashes WHERE fk_id_instance = '$id_instance';" | xargs)
echo "[HASHCAT INFO] wordlists = $wordlists"
## Récuperer l'url_custom_list
url_custom_list=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT custom_wordlist FROM public.hashes WHERE fk_id_instance = '$id_instance';" | xargs)
echo "[HASHCAT INFO] url_custom_list = $url_custom_list"
## Récuperer l'algorithm
algorithm=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT algorithm FROM public.hashes WHERE id_hash='$id_hash';")
echo "[HASHCAT INFO] algorithm = $algorithm"

# Télécharger le fichier de hash depuis S3
## Télécharger l'url
echo "[HASHCAT ACTION] Téléchargement du hash en cours : $url_hash"
if [ -n "$url_hash" ]; then
    wget "$url_hash" -O $path_hash
    echo "[HASHCAT INFO] hash :"
    cat $path_hash
else
    echo "[HASHCAT ERREUR] URL du hash introuvable dans la base de données."
    PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE $TABLE_HASHES SET status='Error' WHERE id_hash = $id_hash;"
    exit 1
fi

# Mettre les wordlist par défaut choisis dans la wordlist final
## Nettoyage des [] de la wordlist
clean_wordlists=$(echo $wordlists | tr -d '[]' | tr -d ' ')
echo "[HASHCAT INFO] Liste wordlist : $clean_wordlists"

# Téléchareger chaque default wordlist depuis S3 
IFS=',' read -r -a wordlists <<< "$clean_wordlists"
for wordlist in "${wordlists[@]}"; do
    echo "[HASHCAT ACTION] Téléchagement de $wordlist en cours..."
    wget "https://$BUCKET_NAME_WORDLIST.s3.amazonaws.com/default-wordlist/$wordlist.txt" -O /tmp/$wordlist.txt
    
    cat /tmp/$wordlist.txt >> $temp_wordlist_file # enelever le head et mettre cat 
done

# Mettre la wordlist custom choisis dans la wordlist final
## Télécharger le fichier de custom worlist depuis S3
if [ -n "$url_custom_list" ]; then
    echo "[HASHCAT ACTION] Ajout de url_custom_list"
    wget "$url_custom_list" -O $custom_worldist_file
    cat "$custom_worldist_file" >> $temp_wordlist_file
else
    echo "[HASHCAT INFO] Aucune url_custom_list"
fi

## Nettoyage de la wordlist
sort $temp_wordlist_file | uniq > $final_wordlist_file
rm $temp_wordlist_file


# hashes.status = Processing
echo "[HASHCAT STATUS] Instance $id_arch: $status_processing"
PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.hashes SET status = '$status_processing' WHERE id_hash = $id_hash;"

# Lancer Hashcat
echo "[HASHCAT ACTION] hashcat $algorithm $path_hash $final_wordlist_file --status -O --status-timer 1 | tee -a $log_hashcat | grep -E 'Progress|Estimated'  > $path_parsed_output_hashcat "
hashcat $algorithm $path_hash $final_wordlist_file --status -O --status-timer 1 | tee -a $log_hashcat | grep -E "Progress|Estimated|Speed"  > $path_parsed_output_hashcat

hashcat $algorithm $path_hash $final_wordlist_file --show
hashcat $algorithm $path_hash $final_wordlist_file --show > $path_result



# Envoyer le result en BDD
## Vérifie le code de sortie de hashcat
HASHCAT_EXIT_CODE=$?
line_count=$(wc -l < path_result)
    # 0 = Not found
    # 1 = Cracked

if [ $HASHCAT_EXIT_CODE -ne 0 ] && [ $HASHCAT_EXIT_CODE -ne 1 ]; then
    # probleme au lancement de hashcat
    echo "[HASHCAT ERREUR] Erreur lors du lancement de hashcat avec le code de retour $HASHCAT_EXIT_CODE"
    PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE $TABLE_HASHES SET status='Error' WHERE id_hash = $id_hash;"
elif [ $line_count -eq 0 ]; then
    # password pas trouvé
    echo "[HASHCAT RESULT] Password Exhausted"
    PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE $TABLE_HASHES SET status='Not Found' WHERE id_hash=$id_hash ;"
else
    # password trouvé
    echo "[HASHCAT RESULT] Password Cracked"

    # Envoyer le password en BDD
    #hash:password
    while IFS=: read -r hash password
    do
        if [ -n "$hash" ] && [ -n "$password" ]; then
            echo "[HASHCAT ACTION] Upload tu mot de passe en BDD"
            aws s3 cp $path_result s3://$BUCKET_NAME_HASH/cracked/result-$id_arch.txt
            url_hash_cracked="https://$BUCKET_NAME_HASH.s3.amazonaws.com/cracked/result-$id_arch.txt"
            #PGPASSWORD="$DB_PASSWORD" psql -U $DB_USERNAME -h $DB_HOST -p $DB_PORT -d $DB_NAME -c "UPDATE $TABLE_HASHES SET result='$password' WHERE id_hash=$id_hash;"
            PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE $TABLE_HASHES SET result='$url_hash_cracked' WHERE id_hash=$id_hash";
            fi
    done < $path_result

fi
