#!/bin/bash
DB_USERNAME="userHash2ash"
DB_PASSWORD="C5yAn39f8Tm7U13z"
DB_HOST="db-hash2ash-prod.c3m2i44y2jm0.us-east-1.rds.amazonaws.com"
DB_PORT="5432"
DB_NAME="hash2ash"

TABLE_HASHES="public.hashes"
path_hash="/tmp/hash.txt"
if [ $# -ne 2 ]; then
    echo "Usage: $0 <id_arch> <id_hash>"
    exit 1
fi

id_arch=$1
id_hash=$2
path_result="/tmp/result-$id_arch.txt"
# =========== Recuperer le Hash depuis S3 ======================================
# Reda uploadera une url dans la table public.hashes.hash
# TODO
# url_hash=select hash from public.hashes where id_hash = $id_hash
# wget $url_hash -O $path_hash
# ...
# modifier le hashcat pour qu il prenne en entré : path_hash 
# ==============================================================================


# =========== Generer wordlist final (defaut + custom) ======================================
temp_wordlist_file="/tmp/wordlist_temp.txt"
final_wordlist_file="/tmp/wordlist.txt"
custom_worldist_file=/tmp/custom_worldist_file.txt

id_instance=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT id_instance FROM public.instances WHERE id_arch='$id_arch';" | xargs)
echo "id_instance = $id_instance"

# Exécuter la requête SQL pour récupérer les wordlists
wordlists=$(PGPASSWORD=$DB_PASSWORD psql -U $DB_USERNAME -h $DB_HOST -p $DB_PORT -d $DB_NAME -t -c "SELECT wordlist FROM public.hashes WHERE fk_id_instance = '$id_instance';")
echo "wordlists = $wordlists"

# Ajouter chaque wordlist locale au fichier temporaire
# Supprimer les [] et espaces
formatted_input=$(echo $wordlists | tr -d '[]' | tr -d ' ')

# Loop through the elements and call process_element.sh with each one
for wordlist in $(echo $formatted_input | tr ',' '\n' | awk -F'"' '{print $2}'); do
    wget "https://hash2ash-wordlist.s3.amazonaws.com/$wordlist.txt" -O /tmp/$wordlist.txt
    cat /tmp/$wordlist.txt >> $temp_wordlist_file
done

url_custom_list=$(PGPASSWORD=$DB_PASSWORD psql -U $DB_USERNAME -h $DB_HOST -p $DB_PORT -d $DB_NAME -t -c "SELECT custom_wordlist FROM public.hashes WHERE fk_id_instance = '$id_instance';"| xargs)
echo "url_custom_list = $url_custom_list"

if [ -n "$url_custom_list" ]; then
    echo "url cutom list exist"
    wget "$url_custom_list" -O $custom_worldist_file
    cat "$custom_worldist_file" >> $temp_wordlist_file
fi

sort $temp_wordlist_file | uniq > $final_wordlist_file
rm $temp_wordlist_file

# ===========================================



# donne le fk_id_instance au hash
id_instance=$(PGPASSWORD='C5yAn39f8Tm7U13z' psql -U userHash2ash -h db-hash2ash-prod.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d hash2ash -t -c "SELECT id_instance FROM public.instances WHERE id_arch = '$id_arch';" | tr -d '[:space:]')
PGPASSWORD='C5yAn39f8Tm7U13z' psql -U userHash2ash -h db-hash2ash-prod.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d hash2ash -c "UPDATE public.hashes SET fk_id_instance=$id_instance WHERE id_hash='$id_hash';"

#hashcat -m 400 /tmp/hash.hash $final_wordlist_file --status -O
hashcat -m 400 /tmp/hash.hash $final_wordlist_file --status -O
# hashcat is processing, wait...

HASHCAT_EXIT_CODE=$?
# 0 = Cracked
# 1 = Not found


# Vérifie le code de sortie de hashcat
if [ $HASHCAT_EXIT_CODE -ne 0 ]; then
    # password pas trouvé
    echo "Password Exhausted"
    PGPASSWORD="$DB_PASSWORD" psql -U $DB_USERNAME -h $DB_HOST -p $DB_PORT -d $DB_NAME -c "UPDATE $TABLE_HASHES SET status='NotFound' WHERE id_hash=$id_hash ;"
else
    # password trouvé
    echo "Password Cracked"
    hashcat -m 400 /tmp/hash.hash $final_wordlist_file --show
    hashcat -m 400 /tmp/hash.hash $final_wordlist_file --show > $path_result

    # Lire le fichier de sortie de Hashcat
    #hash:password
    while IFS=: read -r hash password
    do
        if [ -n "$hash" ] && [ -n "$password" ]; then
            aws s3 cp $path_result s3://hash2ash-hash/$path_result
            url_hash_cracked="https://hash2ash-hash.s3.amazonaws.com/$path_result"
            #PGPASSWORD="$DB_PASSWORD" psql -U $DB_USERNAME -h $DB_HOST -p $DB_PORT -d $DB_NAME -c "UPDATE $TABLE_HASHES SET result='$password' WHERE id_hash=$id_hash;"
            PGPASSWORD="$DB_PASSWORD" psql -U $DB_USERNAME -h $DB_HOST -p $DB_PORT -d $DB_NAME -c "UPDATE $TABLE_HASHES SET result='$url_hash_cracked' WHERE id_hash=$id_hash;"
            
            fi
    done < $path_result

fi

