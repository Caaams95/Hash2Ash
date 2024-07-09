#!/bin/bash
source ../.env

if [ $# -ne 1 ]; then
    echo "Usage: $0 <id_hash>"
    exit 1
fi

id_hash=$1

echo id_hash = $id_hash


status_initialisation="Initialisation"
status_processing="Processing"


# hashes.status = Initialisation
PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.hashes SET status='$status_initialisation' WHERE id_hash='$id_hash';"

# Select power instance needed
power=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT power FROM public.hashes WHERE id_hash = '$id_hash';" | xargs)
echo power : $power

# Initialiser Terraform
terraform init

# Récupérer le nombre actuel d'instances actives dans l'état Terraform
current_count_low=$(terraform state list | grep 'aws_instance.instance_low' | wc -l)
current_count_medium=$(terraform state list | grep 'aws_instance.instance_medium' | wc -l)
current_count_high=$(terraform state list | grep 'aws_instance.instance_high' | wc -l)

if [ "$power" == "Low" ]; then
    type_instance="t2.large"
    new_count=$((current_count_low + 1))
    terraform apply -refresh=false -auto-approve -var="total_instance_count_low=$new_count" -var="total_instance_count_medium=$current_count_medium" -var="total_instance_count_high=$current_count_high"
    # Récupérer les détails des instances créées
    instances_details=$(terraform output -json instances_details_low)

    # Trouver les détails de la dernière instance créée
    latest_instance=$(echo "$instances_details" | jq -c ".[-1]")

    # Récupérer l'adresse IP publique et le nom de la nouvelle instance
    instance_ip=$(echo "$latest_instance" | jq -r '.public_ip')
    instance_name=$(echo "$latest_instance" | jq -r '.name')
    id_arch=$(echo "$latest_instance" | jq -r '.instance_id')

elif [ "$power" == "Medium" ]; then
    type_instance="c5.xlarge"
    new_count=$((current_count_medium + 1))
    terraform apply -refresh=false -auto-approve -var="total_instance_count_low=$current_count_low" -var="total_instance_count_medium=$new_count" -var="total_instance_count_high=$current_count_high"
    # Récupérer les détails des instances créées
    instances_details=$(terraform output -json instances_details_medium)

    # Trouver les détails de la dernière instance créée
    latest_instance=$(echo "$instances_details" | jq -c ".[-1]")

    # Récupérer l'adresse IP publique et le nom de la nouvelle instance
    instance_ip=$(echo "$latest_instance" | jq -r '.public_ip')
    instance_name=$(echo "$latest_instance" | jq -r '.name')
    id_arch=$(echo "$latest_instance" | jq -r '.instance_id')

elif [ "$power" == "High" ]; then
    type_instance="c7a.12xlarge"
    new_count=$((current_count_high + 1))
    terraform apply -refresh=false -auto-approve -var="total_instance_count_low=$current_count_low" -var="total_instance_count_medium=$current_count_medium" -var="total_instance_count_high=$new_count"
    # Récupérer les détails des instances créées
    instances_details=$(terraform output -json instances_details_high)

    # Trouver les détails de la dernière instance créée
    latest_instance=$(echo "$instances_details" | jq -c ".[-1]")

    # Récupérer l'adresse IP publique et le nom de la nouvelle instance
    instance_ip=$(echo "$latest_instance" | jq -r '.public_ip')
    instance_name=$(echo "$latest_instance" | jq -r '.name')
    id_arch=$(echo "$latest_instance" | jq -r '.instance_id')

else
    echo "Power level not recognized"
    exit 1
fi


echo =======================================
echo id_hash = $id_hash
echo instance_ip = $instance_ip
echo instance_name = $instance_name
echo id_arch = $id_arch
echo =======================================


# Insérer l'ID de la nouvelle instance dans la base de données (exemple avec PostgreSQL)
is_processed=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM public.instances WHERE id_arch = '$id_arch';" | tr -d '[:space:]')

if [ "$is_processed" -le 0 ]; then
    # Ajouter l'instance dans la base de données
    PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "INSERT INTO public.instances (type_instance, id_arch, price_provider, price_hash2ash, status) VALUES ('$type_instance', '$id_arch', 2, 4, '$status_processing');"

    # hashes.status = Processing
    PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.hashes SET status = '$status_processing' WHERE id_hash = $id_hash;"


    # Exécuter des commandes sur l'instance créée (exemple avec SSH)
    ssh -o "StrictHostKeyChecking=no" -i /home/cams/.ssh/Cle_test_terraform.pem ubuntu@"$instance_ip" \
        "chmod +x /tmp/ssh_commande_start.sh && \
        /tmp/ssh_commande_start.sh $id_arch $id_hash" 
fi

# Afficher le succès de la création de l'instance
echo "Nouvelle instance créée avec succès. Dernière adresse IP publique : $instance_name : $instance_ip : $power"
