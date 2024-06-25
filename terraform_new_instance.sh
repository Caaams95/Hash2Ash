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


# Attendre que Terraform ait terminé de créer la nouvelle instance
sleep 30

# Récupérer toutes les adresses IP publiques de la nouvelle instance créée
instances_details=($(terraform output -json instances_details | jq -r '.[]'))

# Afficher toutes les adresses IP publiques
#for ip in "${new_instance_ips[@]}"; do
#  echo "Nouvelle instance créée avec succès. Adresse IP publique : $ip"
#done

# Récupérer la dernière adresse IP publique de la nouvelle instance créée
last_instance_ip=${instances_details[-2]}
last_instance_name=${instances_details[-4]}

# Afficher la dernière adresse IP publique
echo "Nouvelle instance créée avec succès. Dernière adresse IP publique : $last_instance_name : $last_instance_ip"
