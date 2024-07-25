#!/bin/bash
source ../.env

# Vérifiez si l'ID de l'instance est passé en argument
if [ $# -ne 1 ]; then
    echo "Usage: $0 <id_arch>"
    exit 1
fi


# ID de l'instance à supprimer
id_arch=$1
id_instance=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT id_instance FROM public.instances WHERE id_arch = '$id_arch';" | xargs)

id_hash=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT id_hash FROM public.hashes WHERE fk_id_instance = '$id_instance';" | xargs)


echo "[INSTANCE ACTION] Arret de l'instance $id_arch en cours"

# use_terraform='1'
PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.hashes SET use_terraform='1' WHERE id_hash='$id_hash';"



# Obtenir la liste des instances gérées par Terraform
terraform_instances=$(terraform state list | grep 'aws_instance.instance-gratuite')

# Trouver l'index de l'instance dans l'état Terraform par son ID AWS
for instance in $terraform_instances; do
  current_id=$(terraform state show $instance | grep "id                                   =" | awk '{print $3}' | tr -d '"')
  if [ "$current_id" == "$id_arch" ]; then
    # Supprimer l'instance de l'état Terraform
    terraform state rm $instance
    break
  fi
done

# Terminer l'instance avec AWS CLI
aws ec2 terminate-instances --instance-ids "$id_arch"

# Mettre à jour le statut dans la base de données
status_shutdown="Terminate"
PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.instances SET date_shutdown=(now() at time zone 'Europe/Paris') WHERE id_arch='$id_arch';"

# use_terraform='0'
PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.hashes SET use_terraform='0' WHERE id_hash='$id_hash';"

# Afficher le succès de la suppression de l'instance
echo "[INSTANCE ACTION] Arret de l'instance $id_arch terminé"
