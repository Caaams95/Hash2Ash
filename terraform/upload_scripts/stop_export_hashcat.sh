#!/bin/bash
source /tmp/.env_script

if [ $# -ne 1 ]; then
    echo "Usage: $0 <id_hash>"
    exit 1
fi

id_hash=$1
SESSION_NAME="session_hash2ash"
HASH_FILE="/tmp/hash.txt"
S3_BUCKET="hash2ash-hash"
WORDLISTS="/tmp/wordlist.txt"

id_instance=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT fk_id_instance FROM public.hashes WHERE id_hash = '$id_hash';" | xargs)
id_arch=$(PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -t -c "SELECT id_arch FROM public.instances WHERE id_instance = '$id_instance';" | xargs)

ZIP_FILE="${SESSION_NAME}_idhash_${id_hash}_idarch_${id_archRe}.zip"
EXPORT_FOLDER="/tmp/session_folder"


# Arrêt de Hashcat
echo 'Arrêt de Hashcat...'
pkill -f "/tmp/get_progress*"
pkill -f "/tmp/cost_*"
pkill -f "hashcat /tmp*"

# Export de la session vers S3
mkdir "$EXPORT_FOLDER"

cp "/home/ubuntu/.local/share/hashcat/hashcat.potfile" "$EXPORT_FOLDER/"
cp "/home/ubuntu/.local/share/hashcat/sessions/${SESSION_NAME}.restore" "$EXPORT_FOLDER/"
cp "/home/ubuntu/.local/share/hashcat/sessions/${SESSION_NAME}.log" "$EXPORT_FOLDER/"
cp "$HASH_FILE" "$EXPORT_FOLDER/"
cp "$WORDLISTS" "$EXPORT_FOLDER/"

# Aller dans le répertoire temporaire et créer le fichier ZIP
cd "$EXPORT_FOLDER"
zip -r "/tmp/$ZIP_FILE" .
cd -

# Supprimer le répertoire temporaire
rm -rf "$EXPORT_FOLDER"

# Télécharger le fichier ZIP sur S3
aws s3 cp "/tmp/$ZIP_FILE" "s3://$S3_BUCKET/session_hashcat/"

# Construire le lien S3 HTTPS
S3_LINK="https://${S3_BUCKET}.s3.amazonaws.com/session_hashcat/${ZIP_FILE}"

# Supprimer le fichier ZIP local
rm "/tmp/$ZIP_FILE"

echo "Session Hashcat exportée et téléchargée sur S3 avec succès."

# Mise à jour de la base de données avec le lien S3
PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.hashes SET session_hashcat='$S3_LINK' WHERE id_hash='$id_hash';"

echo "Lien S3 mis à jour dans la base de données avec succès."

PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USERNAME" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "UPDATE public.hashes SET status='Stopped' WHERE id_hash='$id_hash';"
