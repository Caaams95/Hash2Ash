#!/bin/bash
source ../.env
if [ $# -ne 2 ]; then
    echo "Usage: $0 <id_arch> <status>"
    exit 1
fi

id_arch=$1
status=$2
PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.instances SET status='$status' WHERE id_arch='$id_arch';"
