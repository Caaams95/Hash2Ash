#!/bin/bash

# Informations de connexion
PGPASSWORD='A72gm143kldF47GI'
USER='userHash2ash'
HOST='hash2ash.c3m2i44y2jm0.us-east-1.rds.amazonaws.com'
PORT='5432'
DB='initial_db'
QUERY="SELECT id_hash, result, instance_id FROM information_schema.hashes;"

while true; do
    clear

    # Exécution de la commande PostgreSQL et stockage du résultat
    RESULT=$(PGPASSWORD=$PGPASSWORD psql -U $USER -h $HOST -p $PORT -d $DB -t -c "$QUERY")

    # Boucle sur chaque ligne du résultat
    echo "$RESULT" | while IFS='|' read -r id_hash result instance_id; do
    # Suppression des espaces en début et fin de chaîne
    id_hash=$(echo "$id_hash" | xargs)
    result=$(echo "$result" | xargs)
    
    # Vérification si la chaîne result n'est pas vide
    if [ -n "$result" ]; then
        echo "id_hash: $id_hash, result: $result, instance_id: $instance_id"
        ./terraform_stop_instance.sh $instance_id

    fi
    done
    sleep 1
done