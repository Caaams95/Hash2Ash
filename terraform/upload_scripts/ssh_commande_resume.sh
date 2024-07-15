#!/bin/bash
source /tmp/.env_script

if [ $# -ne 2 ]; then
    echo "Usage: $0 <id_arch> <id_hash>"
    exit 1
fi

id_arch=$1
id_hash=$2

echo "[SSH COMMAND - $id_arch] sudo apt-get update -y"
sudo apt-get update -y

#echo "[SSH COMMAND - $id_arch] sudo apt-get upgrade -y"
#sudo apt-get upgrade -y

echo "[SSH COMMAND - $id_arch] sudo snap install aws-cli --classic"
sudo snap install aws-cli --classic

echo "[SSH COMMAND - $id_arch] aws configure set aws_access_key_id $AWS_ACCESS_KEY"
aws configure set aws_access_key_id $AWS_ACCESS_KEY

echo "[SSH COMMAND - $id_arch] aws configure set aws_secret_access_key $AWS_SECRET_KEY"
aws configure set aws_secret_access_key $AWS_SECRET_KEY

echo "[SSH COMMAND - $id_arch] aws configure set default.region $REGION"
aws configure set default.region $REGION

echo "[SSH COMMAND - $id_arch] sudo apt install postgresql -y"
sudo apt install postgresql -y

echo "[SSH COMMAND - $id_arch] sudo apt-get install zip -y"
sudo apt-get install zip -y

echo "[SSH COMMAND - $id_arch] sudo apt-get install hashcat -y"
sudo apt-get install hashcat -y

echo "[SSH COMMAND - $id_arch] chmod +x /tmp/go_hashcat.sh"
chmod +x /tmp/go_hashcat.sh

echo "[SSH COMMAND - $id_arch] chmod +x /tmp/get_progress_live.sh"
chmod +x /tmp/get_progress_live.sh

echo "[SSH COMMAND - $id_arch] chmod +x /tmp/cost_instance_live.sh"
chmod +x /tmp/cost_instance_live.sh

echo "[SSH COMMAND - $id_arch] chmod +x /tmp/stop_export_hashcat.sh"
chmod +x /tmp/stop_export_hashcat.sh

echo "[SSH COMMAND - $id_arch] sleep 1"
sleep 1

echo "[SSH COMMAND - $id_arch] /tmp/cost_instance_live.sh $id_arch &"
/tmp/cost_instance_live.sh $id_arch &

echo "[SSH COMMAND - $id_arch] sleep 1"
sleep 1

echo "[SSH COMMAND - $id_arch] /tmp/get_progress_live.sh $id_hash &"
/tmp/get_progress_live.sh $id_hash &

echo "[SSH COMMAND - $id_arch] sleep 1"
sleep 1

echo "[SSH COMMAND - $id_arch] /tmp/resume_hashcat.sh $id_arch $id_hash"
/tmp/go_hashcat.sh $id_arch $id_hash
