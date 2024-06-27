#!/bin/bash

status_processing="Processing"

# Initialiser Terraform
terraform init

# Récupérer le nombre actuel d'instances actives dans l'état Terraform
current_count=$(terraform state list | grep 'aws_instance.instance_gratuite' | wc -l)
new_count=$((current_count + 1))

# Appliquer la configuration Terraform avec le nouveau nombre d'instances sans rafraîchir l'état
terraform apply -refresh=false -auto-approve -var="total_instance_count=$new_count"

# Récupérer les détails des instances créées
instances_details=$(terraform output -json instances_details)

# Trouver les détails de la dernière instance créée
latest_instance=$(echo "$instances_details" | jq -c ".[-1]")

# Récupérer l'adresse IP publique et le nom de la nouvelle instance
instance_ip=$(echo "$latest_instance" | jq -r '.public_ip')
instance_name=$(echo "$latest_instance" | jq -r '.name')
instance_id=$(echo "$latest_instance" | jq -r '.instance_id')

# Insérer l'ID de la nouvelle instance dans la base de données (exemple avec PostgreSQL)
is_processed=$(PGPASSWORD="A72gm143kldF47GI" psql -h hash2ash.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -U userHash2ash -d initial_db -p 5432 -t -c "SELECT COUNT(*) FROM information_schema.instance WHERE instance_id = '$instance_id';")

if [ "$is_processed" -le 0 ]; then
    # Ajouter l'instance dans la base de données
    PGPASSWORD="A72gm143kldF47GI" psql -h hash2ash.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -U userHash2ash -d initial_db -p 5432 -c "INSERT INTO information_schema.instance (instance_id, instance_name, instance_ip, status) VALUES ('$instance_id', '$instance_name', '$instance_ip', '$status_processing');"

    # Exécuter des commandes sur l'instance créée (exemple avec SSH)
    ssh -o "StrictHostKeyChecking=no" -i /home/cams/.ssh/Cle_test_terraform.pem ubuntu@"$instance_ip" \
        'sudo apt-get update -y && sudo apt-get upgrade -y && \
        sudo apt install postgresql -y && \
        sudo apt-get install hashcat -y && \
        chmod +x /tmp/script.sh && \
        /tmp/script.sh'
fi

# Afficher le succès de la création de l'instance
echo "Nouvelle instance créée avec succès. Dernière adresse IP publique : $instance_name : $instance_ip"
