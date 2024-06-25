#!/bin/bash

# Définir les variables
HASH_FILE="lib/hash.hash"
DICT_FILE="lib/example.dict"
HASH_TYPE=400 # Remplacez par le type de hash approprié, par exemple 0 pour MD5
#DB_USER="votre_utilisateur"
#DB_PASSWORD="votre_mot_de_passe"
DB_NAME="test"
DB_TABLE="Hashes"

# Récupérer l'ID du hash le plus récent
id=$(sudo mariadb -N -s -e "SELECT MAX(id_hash) FROM $DB_TABLE;" $DB_NAME)
# sudo mariadb -N -s -e "SELECT MAX(id_hash) FROM Hashes;" test)


# Exécuter Hashcat
hashcat -m $HASH_TYPE $HASH_FILE $DICT_FILE --show > hashcat_output.txt
# hashcat -m 500 -a 0 lib/example500.hash lib/example.dict --show > hashcat_output.txt


# Lire le fichier de sortie de Hashcat
while IFS=: read -r hash password
do
    if [ -n "$hash" ] && [ -n "$password" ]; then
            # Mettre à jour la base de données en une seule ligne
        sudo mariadb $DB_NAME -e "UPDATE $DB_TABLE SET result='$password' WHERE id_hash=$id;"
        # sudo mariadb test -e "UPDATE Hashes SET result='Hash234' WHERE id_hash=4;"
        fi
done < hashcat_output.txt

echo "Base de données mise à jour avec succès."
