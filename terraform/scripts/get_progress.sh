#!/bin/bash
source /tmp/.env_script

if [ $# -ne 1 ]; then
    echo "Usage: $0 <id_hash>"
    exit 1
fi

id_hash=$1
path_clean_output=/tmp/clean_output.txt

touch $path_clean_output
while true
do 
    
    progress=$(tail -n 2 $path_clean_output | sed -n '2p' | cut -d: -f 2)
    PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c  "UPDATE public.hashes SET progress ='$progress' WHERE id_hash='$id_hash';"
    sleep 1
done