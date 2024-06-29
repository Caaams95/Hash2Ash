#!/bin/bash
DB_USERNAME="userHash2ash"
DB_PASSWORD="C5yAn39f8Tm7U13z"
DB_HOST="db-hash2ash-prod.c3m2i44y2jm0.us-east-1.rds.amazonaws.com"
DB_PORT="5432"
DB_NAME="hash2ash"

TABLE_HASHES="public.hashes"

if [ $# -ne  ]; then
    echo "Usage: $0 <id_arch>"
    exit 1
fi

id_arch=$1
id_hash=$2

# donne le fk_id_instance au hash
id_instance=$(PGPASSWORD='C5yAn39f8Tm7U13z' psql -U userHash2ash -h db-hash2ash-prod.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d hash2ash -t -c "SELECT id_instance FROM public.instances WHERE id_arch = '$id_arch';" | tr -d '[:space:]')
PGPASSWORD='C5yAn39f8Tm7U13z' psql -U userHash2ash -h db-hash2ash-prod.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d hash2ash -c "UPDATE public.hashes SET fk_id_instance=$id_instance WHERE id_hash='$id_hash';"

hashcat -m 400 /tmp/hash.hash /tmp/example.dict --status -O
# hashcat is processing, wait...

HASHCAT_EXIT_CODE=$?
# 0 = Cracked
# 1 = Not found



# Vérifie le code de sortie de hashcat
if [ $HASHCAT_EXIT_CODE -ne 0 ]; then
    # password pas trouvé
    PGPASSWORD="$DB_PASSWORD" psql -U $DB_USERNAME -h $DB_HOST -p $DB_PORT -d $DB_NAME -c "UPDATE $TABLE_HASHES SET status='Not Found' WHERE id_hash=$id_hash ;"
else
    # password trouvé
    hashcat -m 400 /tmp/hash.hash /tmp/example.dict --show
    hashcat -m 400 /tmp/hash.hash /tmp/example.dict --show > /tmp/result.txt

    # Lire le fichier de sortie de Hashcat
    #hash:password
    while IFS=: read -r hash password
    do
        if [ -n "$hash" ] && [ -n "$password" ]; then
            # Mettre à jour la base de données en une seule ligne
            PGPASSWORD="$DB_PASSWORD" psql -U $DB_USERNAME -h $DB_HOST -p $DB_PORT -d $DB_NAME -c "UPDATE $TABLE_HASHES SET result='$password' WHERE id_hash=$id_hash;"
            fi
    done < /tmp/result.txt

fi

