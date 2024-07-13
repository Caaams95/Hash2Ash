#!/bin/bash
source /tmp/.env_script

if [ $# -ne 2 ]; then
    echo "Usage: $0 <id_arch> <id_hash>"
    exit 1
fi

id_arch=$1
id_hash=$2


sudo apt-get update -y
sudo apt-get upgrade -y
sudo snap install aws-cli --classic
aws configure set aws_access_key_id $AWS_ACCESS_KEY
aws configure set aws_secret_access_key $AWS_SECRET_KEY
aws configure set default.region $REGION
sudo apt install postgresql -y
sudo apt-get install hashcat -y
chmod +x /tmp/go_hashcat.sh
chmod +x /tmp/get_progress_live.sh
chmod +x /tmp/cost_instance_live.sh
sleep 1
/tmp/cost_instance_live.sh $id_arch &
sleep 1
/tmp/get_progress_live.sh $id_hash &
sleep 1
/tmp/go_hashcat.sh $id_arch $id_hash
