#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 <id_arch> <id_hash>"
    exit 1
fi

DB_USERNAME="userHash2ash"
DB_PASSWORD="C5yAn39f8Tm7U13z"
DB_HOST="db-hash2ash-prod.c3m2i44y2jm0.us-east-1.rds.amazonaws.com"
DB_PORT="5432"
DB_NAME="hash2ash"
TABLE_HASHES="public.hashes"

id_arch=$1
id_hash=$2

path_hash="/tmp/hash.txt"
path_result="/tmp/result-$id_arch.txt"

temp_wordlist_file="/tmp/wordlist_temp.txt"
final_wordlist_file="/tmp/wordlist.txt"
custom_worldist_file="/tmp/custom_worldist_file.txt"


# Récuperation de id_instance selon le id_arch 
id_instance=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT id_instance FROM public.instances WHERE id_arch='$id_arch';")
echo id_instance = $id_instance
# Mise à jour de la BDD : fk_id_instance = id_instance
PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.hashes SET fk_id_instance=$id_instance WHERE id_hash='$id_hash';"
## Récuperer l'url_hash
url_hash=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT hash FROM public.hashes WHERE id_hash = $id_hash;" | xargs)
echo url_hash = $url_hash
## Récuperation de la wordlist en BDD
wordlists=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT wordlist FROM public.hashes WHERE fk_id_instance = '$id_instance';" | xargs)
echo wordlists = $wordlists
## Récuperer l'url_custom_list
url_custom_list=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT custom_wordlist FROM public.hashes WHERE fk_id_instance = '$id_instance';" | xargs)
echo url_custom_list = $url_custom_list
## Récuperer l'algorithm
algorithm=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT algorithm FROM public.hashes WHERE id_hash='$id_hash';")
echo algorithm = $algorithm

# Télécharger le fichier de hash depuis S3
## Télécharger l'url
echo Téléchargement du hash en cours : $url_hash
if [ -n "$url_hash" ]; then
    wget "$url_hash" -O $path_hash
    echo hash :
    cat $path_hash
else
    echo "URL du hash introuvable dans la base de données."
    exit 1
fi

# Mettre les wordlist par défaut choisis dans la wordlist final
## Nettoyage des [] de la wordlist
clean_wordlists=$(echo $wordlists | tr -d '[]' | tr -d ' ')
echo clean_wordlists : $clean_wordlists

# Téléchareger chaque default wordlist depuis S3 
IFS=',' read -r -a wordlists <<< "$clean_wordlists"
for wordlist in "${wordlists[@]}"; do
    echo Téléchagement de $wordlist en cours...
    wget "https://hash2ash-wordlist.s3.amazonaws.com/$wordlist.txt" -O /tmp/$wordlist.txt
    cat /tmp/$wordlist.txt >> $temp_wordlist_file # enelever le head et mettre cat 
done

# Mettre la wordlist custom choisis dans la wordlist final
## Télécharger le fichier de custom worlist depuis S3
if [ -n "$url_custom_list" ]; then
    echo " Ajout de url_custom_list"
    wget "$url_custom_list" -O $custom_worldist_file
    cat "$custom_worldist_file" >> $temp_wordlist_file
else
    echo " Aucune url_custom_list"
fi

## Nettoyage de la wordlist
sort $temp_wordlist_file | uniq > $final_wordlist_file
rm $temp_wordlist_file

# Lancer Hashcat
echo "hashcat -m $algorithm $path_hash $final_wordlist_file --status -O"
hashcat -m $algorithm $path_hash $final_wordlist_file --status -O
hashcat -m $algorithm $path_hash $final_wordlist_file --show
hashcat -m $algorithm $path_hash $final_wordlist_file --show > $path_result

# Envoyer le result en BDD
## Vérifie le code de sortie de hashcat
# HASHCAT_EXIT_CODE=$?
line_count=$(wc -l < path_result)



    # 0 = Cracked
    # 1 = Not found
if [ $line_count -eq 0 ]; then
    # password pas trouvé
    echo "Password Exhausted"
    PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE $TABLE_HASHES SET status='NotFound' WHERE id_hash=$id_hash ;"
else
    # password trouvé
    echo "Password Cracked"

    # Envoyer le password en BDD
    # Lire le fichier de sortie de Hashcat
    #hash:password
    while IFS=: read -r hash password
    do
        if [ -n "$hash" ] && [ -n "$password" ]; then
            aws s3 cp $path_result s3://hash2ash-hash/cracked/result-$id_arch.txt
            url_hash_cracked="https://hash2ash-hash.s3.amazonaws.com/cracked/result-$id_arch.txt"
            #PGPASSWORD="$DB_PASSWORD" psql -U $DB_USERNAME -h $DB_HOST -p $DB_PORT -d $DB_NAME -c "UPDATE $TABLE_HASHES SET result='$password' WHERE id_hash=$id_hash;"
            PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE $TABLE_HASHES SET result='$url_hash_cracked' WHERE id_hash=$id_hash";
            fi
    done < $path_result

fi
