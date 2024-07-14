#!/bin/bash
source /tmp/.env_script

if [ $# -ne 1 ]; then
    echo "Usage: $0 <id_hash>"
    exit 1
fi

id_hash=$1
# SELECT information BDD
id_instance=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT fk_id_instance FROM public.hashes WHERE id_hash='$id_hash';" | xargs)
ip_instance=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT ip FROM public.instances WHERE id_instance='$id_instance';" | xargs)

# Arret de Hashcat
echo 'Arrêt de Hashcat...'
pkill -f "/tmp/get_progress*"
pkill -f "/tmp/cost_*"
pkill -f "hashcat /tmp*"


# Export de la session vers S3
# TODO

# Changement de hashes.status
PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.hashes SET status="Stopped" WHERE id_hash='$id_hash';"
