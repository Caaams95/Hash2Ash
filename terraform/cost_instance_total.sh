#!/bin/bash

# Définir la locale pour s'assurer que les nombres avec des points décimaux sont correctement interprétés
# permet d'eviter les bug de : 99,99$ ici la "," pose probleme car en temps normal il faut un "." donc on passe en en_US.UTF-8
export LC_NUMERIC="en_US.UTF-8"

source ../.env
if [ $# -ne 1 ]; then
    echo "Usage: $0 <id_arch> "
    exit 1
fi

id_arch=$1

# Définir les deux dates
DATE_START=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT date_start FROM public.instances WHERE id_arch='$id_arch';" | xargs)
DATE_END=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT date_shutdown FROM public.instances WHERE id_arch='$id_arch';" | xargs)

echo "================= GET INFORMATION =================="
id_instance=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT id_instance FROM public.instances WHERE id_arch='$id_arch';" | xargs)
echo "id_instance=$id_instance"
# Récupération du prix de l'instance par heure
power=$(PGPASSWORD="C5yAn39f8Tm7U13z" psql -U "userHash2ash" -h "db-hash2ash-prod.c3m2i44y2jm0.us-east-1.rds.amazonaws.com" -p "5432" -d "hash2ash" -t -c "SELECT power FROM public.hashes WHERE fk_id_instance = '$id_instance';" | xargs)
echo "power=$power"
provider=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT provider FROM public.hashes WHERE fk_id_instance = '$id_instance';" | xargs)
echo provider=$provider
price_instance_hash2ash=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT price_hash2ash FROM public.conf_instance WHERE power = '$power' AND provider = '$provider';" | xargs)
echo "price_instance_hash2ash=$price_instance_hash2ash"
echo "===================================="


echo "========================== CALCUL DU PRIX FINAL =========================="
echo id_arch = $id_arch
echo id_instance = $id_instance
echo DATE_START = $DATE_START
echo DATE_END = $DATE_END

# Convertir les dates en secondes depuis l'époque (Epoch)
SECONDS1=$(date -d "$DATE_START" +%s.%N)
SECONDS2=$(date -d "$DATE_END" +%s.%N)

# Calculer la différence
DIFF=$(awk -v d1="$SECONDS1" -v d2="$SECONDS2" 'BEGIN {print int(d2 - d1)}')

# Convertir la différence en un format lisible (heures, minutes, secondes)
HOURS=$(echo "$DIFF / 3600" | bc)
MINUTES=$(echo "($DIFF % 3600) / 60" | bc)
SECONDS=$(echo "$DIFF % 60" | bc)

# Calculer le coût total en tenant compte des heures décimales
HOURS_COST=$(echo "$HOURS * $price_instance_hash2ash" | bc -l)
MINUTES_COST=$(echo "$MINUTES / 60 * $price_instance_hash2ash" | bc -l)
SECONDS_COST=$(echo "$SECONDS / 3600 * $price_instance_hash2ash" | bc -l)  # Correction: / 3600 pour les secondes

TOTAL_COST=$(echo "$HOURS_COST + $MINUTES_COST + $SECONDS_COST" | bc -l)
echo "prix total brut = $TOTAL_COST"

# Arrondir au supérieur et formater à deux chiffres après la virgule
TOTAL_COST=$(echo "$TOTAL_COST + 0.005" | bc -l)
echo "prix total arrondi brut = $TOTAL_COST"

TOTAL_COST=$(printf "%.2f" "$TOTAL_COST")
echo "prix total 2 chiffre après la virgule = $TOTAL_COST"

# Afficher le coût total
echo " "
echo "Cout par heure : $price_instance_hash2ash $"
echo "Temps d'activité : $HOURS h - $MINUTES min - $SECONDS s"

echo "Cout heures = $HOURS_COST $"
echo "Cout minutes = $MINUTES_COST $"
echo "Cout secondes = $SECONDS_COST $"
echo "Le coût total pour la période entre $DATE_START et $DATE_END est de $TOTAL_COST $"

# Mettre à jour la base de données avec le coût total en entier
PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.instances SET price_total='$TOTAL_COST' WHERE id_arch='$id_arch';"
echo "========================== FIN CALCUL DU PRIX =========================="


24h = 240
48h = 480
36h = 360 



8h utiliser
12 heures a remboursé
12



res = €consomé mod €24h
a rembourser = €24€ - res

prix
10€/h

prix 24h = 240€


payé :
72h = 720€

consomé :
69h = 690€

a remboursé:
3h 30€




consomé :
69h = 690€
prix 24h = 240€

690 mod 240 = 210
240 - 210 = 30




24h = 240
4h = 40





res = €consomé mod €24h
a rembourser = €24€ - res

prerequis:
power = select dans l'instance where id.....

calcul temp:
€consomé = instances.price_total
€24h = 24 * (conf_instance.price_has2ash Where power=$power)
res =$€consomé % $€24h

calcul final :
refund = res - $€24h


def get_refund(id_instance)
    return price_refund

def stripe_refund(id, amount)

stripe_refund(SELECT id bdd, get_refund(id_instance:150))