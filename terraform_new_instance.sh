#!/bin/bash

# Vérifier si l'argument du chemin du fichier est fourni
if [ $# -ne 1 ]; then
    echo "Usage: $0 <path_to_script>"
    exit 1
fi

# Récupérer le chemin du fichier script à téléverser et exécuter
script_path=$1

# Initialiser Terraform
terraform init

# Récupérer le nombre actuel d'instances
current_count=$(terraform state list | grep 'aws_instance.instance-gratuite' | wc -l)
new_count=$((current_count + 1))

# Modifier la configuration Terraform pour ajouter une nouvelle instance
terraform apply -auto-approve -var="instance_count=$new_count" -var="script_path=$script_path"


# Récupérer les détails des instances créées
instances_details=$(terraform output -json instances_details)


# Pour chaque nouvelle instance créée
for instance_detail in $(echo "${instances_details}" | jq -c '.[]'); do
    # Récupérer l'adresse IP publique et le nom de l'instance
    instance_ip=$(echo "${instance_detail}" | jq -r '.public_ip')
    instance_name=$(echo "${instance_detail}" | jq -r '.name')
    instance_id=$(echo "${instance_detail}" | jq -r '.instance_id')


    is_processed=$(PGPASSWORD="A72gm143kldF47GI" psql -h hash2ash.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -U userHash2ash -d initial_db -p 5432 -t -c "SELECT COUNT(*) FROM information_schema.instance WHERE instance_id = '$instance_id';")    # Insérer l'ID de l'instance dans la base de données (exemple avec PostgreSQL)
    
    if [ "$is_processed" -le 0 ]; then
        # Exécuter hashcat en arrière-plan sur l'instance créée
        ssh -o "StrictHostKeyChecking=no" -i /home/cams/.ssh/Cle_test_terraform.pem ubuntu@"$instance_ip" \
            'sudo apt-get update -y && sudo apt-get upgrade -y && \
            sudo apt install postgresql -y && \
            sudo apt-get install hashcat -y && \
            chmod +x /tmp/script.sh && \
            /tmp/script.sh > /tmp/hash2ash.log 2>&1'
        
        # AJouter l'instance dans la BDD
        PGPASSWORD="A72gm143kldF47GI" psql -h hash2ash.c3m2i44y2jm0.us-east-1.rds.amazonaws.com -U userHash2ash -d initial_db -p 5432 -c "INSERT INTO information_schema.instance (instance_id, instance_name, instance_ip, status) VALUES ('$instance_id', '$instance_name', '$instance_ip', 1);"

        # Afficher un message indiquant que le bruteforce a démarré sur l'instance
        echo "Bruteforce démarré en arrière-plan sur l'instance $instance_name avec l'adresse IP $instance_ip"
    fi
done

# Afficher le succès de la création de l'instance finale
echo "Nouvelle instance créée avec succès. Dernière adresse IP publique : $instance_name : $instance_ip"