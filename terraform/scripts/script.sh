#!/bin/bash
DB_USERNAME="userHash2ash"
DB_PASSWORD="C5yAn39f8Tm7U13z"
DB_HOST="db-hash2ash-prod.c3m2i44y2jm0.us-east-1.rds.amazonaws.com"
DB_PORT="5432"
DB_NAME="hash2ash"

TABLE_HASHES="public.hashes"



hashcat -m 400 /tmp/hash.hash /tmp/example.dict --status -O
# hashcat is processing, wait...

HASHCAT_EXIT_CODE=$?
# 0 = Cracked
# 1 = Not found



# Vérifie le code de sortie de hashcat
if [ $HASHCAT_EXIT_CODE -ne 0 ]; then
    PGPASSWORD="$DB_PASSWORD" psql -U $DB_USERNAME -h $DB_HOST -p $DB_PORT -d $DB_NAME -c "UPDATE publilc.hashes SET status='Not Found' WHERE id_hash=(SELECT MAX(id_hash) FROM $TABLE_HASHES);"
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
            PGPASSWORD="$DB_PASSWORD" psql -U $DB_USERNAME -h $DB_HOST -p $DB_PORT -d $DB_NAME -c "UPDATE $TABLE_HASHES SET result='$password' WHERE id_hash=(SELECT MAX(id_hash) FROM $TABLE_HASHES);"
            fi
    done < /tmp/result.txt

fi