#!/bin/bash
DB_USERNAME="userHash2ash"
DB_PASSWORD="C5yAn39f8Tm7U13z"
DB_HOST="db-hash2ash-prod.c3m2i44y2jm0.us-east-1.rds.amazonaws.com"
DB_PORT="5432"
DB_NAME="hash2ash"


if [ $# -ne 1 ]; then
    echo "Usage: $0 <id_hash>"
    exit 1
fi

id_hash=$1
echo id_hash = $id_hash



status_initialisation="Initialisation"
status_processing="Processing"

# Initialisation hashes.status
PGPASSWORD='C5yAn39f8Tm7U13z' psql -U userHash2ash -h db-hash2ash-prod.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d hash2ash -c "UPDATE public.hashes SET status='$status_initialisation' WHERE id_hash='$id_hash';"

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
id_arch=$(echo "$latest_instance" | jq -r '.instance_id')

# Insérer l'ID de la nouvelle instance dans la base de données (exemple avec PostgreSQL)
is_processed=$(PGPASSWORD='C5yAn39f8Tm7U13z' psql -U userHash2ash -h db-hash2ash-prod.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d hash2ash -t -c "SELECT COUNT(*) FROM public.instances WHERE id_arch = '$id_arch';" | tr -d '[:space:]')

if [ "$is_processed" -le 0 ]; then
    # Ajouter l'instance dans la base de données
    PGPASSWORD='C5yAn39f8Tm7U13z' psql -U userHash2ash -h db-hash2ash-prod.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -p 5432 -d hash2ash -c "INSERT INTO public.instances (type_instance, id_arch, price_provider, price_hash2ash, status) VALUES ('t2.large', '$id_arch', 2, 4, '$status_processing');"

    # Exécuter des commandes sur l'instance créée (exemple avec SSH)
    ssh -o "StrictHostKeyChecking=no" -i /home/cams/.ssh/Cle_test_terraform.pem ubuntu@"$instance_ip" \
        "sudo apt-get update -y && sudo apt-get upgrade -y && \
        sudo apt install postgresql -y && \
        sudo apt-get install hashcat -y && \
        chmod +x /tmp/script.sh && \
        /tmp/script.sh $id_arch $id_hash"
fi

# Afficher le succès de la création de l'instance
echo "Nouvelle instance créée avec succès. Dernière adresse IP publique : $instance_name : $instance_ip"
