#!/bin/bash
source /tmp/.env_script

if [ $# -ne 1 ]; then
    echo "Usage: $0 <id_hash>"
    exit 1
fi

id_hash=$1
path_parsed_output_hashcat=/tmp/parsed_output_hashcat.txt

touch $path_parsed_output_hashcat
while true
do 
    if [ $(wc -l < $path_parsed_output_hashcat) -gt 5 ]; then 
        progress=$(tac $path_parsed_output_hashcat | grep Progress | head -n 5 | sed -ne '2p' | cut -d: -f 2 | xargs)
        time_estimated=$(tac $path_parsed_output_hashcat | grep Estimated | head -n 5 | sed -ne '2p' | awk -F '[()]' '/Time.Estimated...:/ {print $2}' | xargs)
        hash_per_second=$(tac $path_parsed_output_hashcat | grep Speed |  head -n 5 | sed -ne '2p' | cut -d'(' -f 1 | cut -d : -f2 | xargs)
        cat /tmp/log_hashcat.txt

        echo "[PROGESS] progress id_hash $id_hash = $progress"

        PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c  "UPDATE public.hashes SET progress ='$progress' WHERE id_hash='$id_hash';"
        PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c  "UPDATE public.hashes SET time_estimated ='$time_estimated' WHERE id_hash='$id_hash';"
        PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c  "UPDATE public.hashes SET hash_per_second ='$hash_per_second' WHERE id_hash='$id_hash';"
    fi
    sleep 5
done