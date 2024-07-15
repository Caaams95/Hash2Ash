#!/bin/bash
source ../.env

# Vérifiez si l'ID de l'instance est passé en argument
if [ $# -ne 1 ]; then
    echo "Usage: $0 <id_arch>"
    exit 1
fi

# ID de l'instance à supprimer
instance_id=$1

echo "[INSTANCE ACTION] Arret de l'instance $instance_id en cours"


# Obtenir la liste des instances gérées par Terraform
terraform_instances=$(terraform state list | grep 'aws_instance.instance-gratuite')

# Trouver l'index de l'instance dans l'état Terraform par son ID AWS
for instance in $terraform_instances; do
  current_id=$(terraform state show $instance | grep "id                                   =" | awk '{print $3}' | tr -d '"')
  if [ "$current_id" == "$instance_id" ]; then
    # Supprimer l'instance de l'état Terraform
    terraform state rm $instance
    break
  fi
done

# Terminer l'instance avec AWS CLI
aws ec2 terminate-instances --instance-ids "$instance_id"

# Mettre à jour le statut dans la base de données
status_shutdown="Terminate"
PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.instances SET date_shutdown=(now() at time zone 'Europe/Paris') WHERE id_arch='$instance_id';"

# Afficher le succès de la suppression de l'instance
echo "[INSTANCE ACTION] Arret de l'instance $instance_id terminé"
