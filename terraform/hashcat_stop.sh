#!/bin/bash
source ../.env

if [ $# -ne 1 ]; then
    echo "Usage: $0 <id_hash>"
    exit 1
fi

id_hash=$1

id_instance=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT fk_id_instance FROM public.hashes WHERE id_hash='$id_hash';" | xargs)
ip_instance=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT ip FROM public.instances WHERE id_instance='$id_instance';" | xargs)

echo "id_instance=$id_instance"
echo "ip_instance=$ip_instance"

SSH_KEY="/home/cams/.ssh/Cle_test_terraform.pem"

# Commande à exécuter sur la machine distante pour arrêter Hashcat proprement
STOP_COMMAND=$(cat <<EOF
/tmp/stop_export_hashcat.sh $id_hash
EOF
)

# Exécution de la commande STOP_COMMAND sur l'instance
ssh -o "StrictHostKeyChecking=no" -i "$SSH_KEY" ubuntu@"$ip_instance" "$STOP_COMMAND"
echo "Commande d'arrêt de Hashcat exécutée sur l'instance $id_instance : $ip_instance"
