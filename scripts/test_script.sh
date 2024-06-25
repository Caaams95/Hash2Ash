#!/bin/bash

echo "Processing..." > /tmp/status.txt

# Exécuter Hashcat
hashcat -m 400 /tmp/hash.hash /tmp/example.dict --show > /tmp/hashcat_output.txt

# Lire le fichier de sortie de Hashcat
while IFS=: read -r hash password
do
    if [ -n "$hash" ] && [ -n "$password" ]; then
        # Mettre à jour la base de données en une seule ligne
        echo " UPDATE information_schema.hashes SET result='$password' WHERE id_hash=1;" > /tmp/commande.sql
        PGPASSWORD='A72gm143kldF47GI' psql -U userHash2ash -h hash2ash.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d initial_db -f /tmp/commande.sql
        echo "Finish" > /tmp/status.txt
        fi
done < /tmp/hashcat_output.txt


