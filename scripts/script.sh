#!/bin/bash
DB_USERNAME="userHash2ash"
DB_PASSWORD=" "
DB_DNS="hash2ash.c3m2i44y2jm0.us-east-1.rds.amazonaws.com"
DB_PORT="5432"
DB_NAME="initial_db"

DB_TABLE="information_schema.hashes"

echo "Processing" > /tmp/status.txt

hashcat -m 400 /tmp/hash.hash /tmp/example.dict --status -O
hashcat -m 400 /tmp/hash.hash /tmp/example.dict --show
hashcat -m 400 /tmp/hash.hash /tmp/example.dict --show > /tmp/result.txt

# Lire le fichier de sortie de Hashcat
while IFS=: read -r hash password
do
    if [ -n $"hash" ] && [ -n "$password" ]; then
        # Mettre à jour la base de données en une seule ligne
        echo "UPDATE $DB_TABLE SET result='$password' WHERE id_hash=(SELECT MAX(id_hash) FROM $DB_TABLE);" > /tmp/commande.sql
        PGPASSWORD="$DB_PASSWORD" psql -U $DB_USERNAME -h $DB_DNS -p $DB_PORT -d $DB_NAME -f /tmp/commande.sql
        echo "Finish" > /tmp/status.txt
        fi
done < /tmp/result.txt
