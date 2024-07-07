#!/bin/bash

# Vérifiez que l'ID de l'instance est passé en argument
if [ $# -ne 1 ]; then
    echo "Usage: $0 <Instance-ID>"
    exit 1
fi

INSTANCE_ID=$1

# Obtenir la date de lancement de l'instance
START_DATE=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].LaunchTime' --output text | cut -d'T' -f1)
# Obtenir la date actuelle
END_DATE=$(date +%Y-%m-%d)

echo "START_DATE= $START_DATE"
echo "END_DATE = $END_DATE"

# Obtenir le linked account id
LINKED_ACCOUNT=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].OwnerId' --output text)

# Récupérer le coût depuis la date de lancement jusqu'à aujourd'hui
COST=$(aws ce get-cost-and-usage \
    --time-period Start=$START_DATE,End=$END_DATE \
    --granularity DAILY \
    --filter '{"And":[{"Dimensions":{"Key":"LINKED_ACCOUNT","Values":["'$LINKED_ACCOUNT'"]}},{"Dimensions":{"Key":"SERVICE","Values":["Amazon Elastic Compute Cloud - Compute"]}}]}' \
    --metrics "BlendedCost" \
    --query 'ResultsByTime[*].Total.BlendedCost.Amount' \
    --output text)

# Calculer le coût total
TOTAL_COST=0
for daily_cost in $COST; do
    TOTAL_COST=$(echo "$TOTAL_COST + $daily_cost" | bc)
done

echo "Le coût total de l'instance $INSTANCE_ID depuis sa création est de \$$TOTAL_COST"
