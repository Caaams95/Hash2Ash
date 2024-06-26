#!/bin/bash

# Vérifier si l'argument du chemin du fichier est fourni
if [ $# -ne 1 ]; then
    echo "Usage: $0 <instance_id>"
    exit 1
fi

# Instance ID à supprimer
instance_id=$1


# Trouver l'index de l'instance dans l'état Terraform
instance_index=$(terraform state list | grep 'aws_instance.instance-gratuite' | grep -o '\[.*\]' | tr -d '[]')

# Si l'instance existe dans l'état Terraform, la supprimer de l'état
if [ -n "$instance_index" ]; then
  terraform state rm "aws_instance.instance-gratuite[$instance_index]"
fi

# Terminer l'instance avec AWS CLI
aws ec2 terminate-instances --instance-ids "$instance_id"

# Appliquer la configuration Terraform pour valider les changements
terraform apply -auto-approve

PGPASSWORD='A72gm143kldF47GI' psql -U userHash2ash -h hash2ash.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d initial_db -c "UPDATE information_schema.instance SET status='0' WHERE instance_id=$instance_id;"
