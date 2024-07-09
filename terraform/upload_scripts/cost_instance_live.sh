#!/bin/bash

# Définir la locale pour s'assurer que les nombres avec des points décimaux sont correctement interprétés
# permet d'eviter les bug de : 99,99€ ici la "," pose probleme car en temps normal il faut un "." donc on passe en en_US.UTF-8
export LC_NUMERIC="en_US.UTF-8"

source /tmp/.env_script
if [ $# -ne 1 ]; then
    echo "Usage: $0 <id_arch> "
    exit 1
fi

id_arch=$1
id_instance=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT id_instance FROM public.instances WHERE id_arch='$id_arch';" | xargs)

# Définir la date de début
DATE_START=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT date_start FROM public.instances WHERE id_arch='$id_arch';" | xargs)
price=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT price_hash2ash FROM public.instances WHERE id_arch='$id_arch';" | xargs)


while true
do 
    DATE_END=$(date +'%Y-%m-%d %H:%M:%S')  # Utiliser la date actuelle comme date de fin

    echo "========================== CALCUL DU PRIX =========================="
    echo id_arch = $id_arch
    echo id_instance = $id_instance
    echo DATE_START = $DATE_START
    echo CURRENT DATE = $DATE_END

    # Convertir les dates en secondes depuis l'époque (Epoch)
    SECONDS1=$(date -d "$DATE_START" +%s.%N)
    SECONDS2=$(date -d "$DATE_END" +%s.%N)

    # Calculer la différence
    DIFF=$(awk -v d1="$SECONDS1" -v d2="$SECONDS2" 'BEGIN {print d2 - d1}')

    # Convertir la différence en un format lisible (heures, minutes, secondes)
    HOURS=$(echo "$DIFF / 3600" | bc)
    MINUTES=$(echo "($DIFF % 3600) / 60" | bc)
    SECONDS=$(echo "$DIFF % 60" | bc)

    # Calculer le coût total en tenant compte des heures décimales
    HOURS_COST=$(echo "$HOURS * $price" | bc -l)
    MINUTES_COST=$(echo "$MINUTES / 60 * $price" | bc -l)
    SECONDS_COST=$(echo "$SECONDS / 3600 * $price" | bc -l)  # Correction: / 3600 pour les secondes

    TOTAL_COST=$(echo "$HOURS_COST + $MINUTES_COST + $SECONDS_COST" | bc -l)

    # Arrondir au supérieur et formater à deux chiffres après la virgule
    TOTAL_COST=$(echo "$TOTAL_COST + 0.005" | bc -l)
    TOTAL_COST=$(printf "%.2f" "$TOTAL_COST")

    # Afficher le coût total
    echo " "
    echo "Cout par heure : $price €"
    echo "Temps d'activité : $HOURS h - $MINUTES min - $SECONDS s"

    echo "Cout heures = $HOURS_COST €"
    echo "Cout minutes = $MINUTES_COST €"
    echo "Cout secondes = $SECONDS_COST €"
    echo "Le coût total pour la période entre $DATE_START et $DATE_END est de $TOTAL_COST €"

    # Mettre à jour la base de données avec le coût total en entier
    PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.instances SET price_total='$TOTAL_COST' WHERE id_arch='$id_arch';"
    echo "========================== FIN CALCUL DU PRIX =========================="

    sleep 5
done
