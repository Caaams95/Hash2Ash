# Roadmap des scripts

***A noter que le script terraform importe le script bruteforce, le fichier de conf utilisateur et le package d'hashcat. En plus, il execute le script bruteforce***

## Script initiateur
    1. Variabilisation des différents type de script terraform importation des différent fichier
    2. Récupération du Provider et de l'instance à utiliser depuis le fichier de conf
    3. Création du fichier terraform conforme au exigence d'instance et de provider
    4. Lancement des commandes terraform pour exécuter le second script

## Script Bruteforce
    1. Variabilisation des différentes données necessaire du fichier de conf
    2. Création de la commande de brute force avec hashcat en insérant les données utilisateur (hash et condition de déchiffrement)
    3. Execution de la commande et attente
    4. Récupération du statut afficher par hashcat, le parser et le renvoyer
    5. Si le statut vaut cracked arréter le script et renvoyer les différents résultat

***Point à réfléchir*** : 

- ***Bonus :*** Sauvegardes d'une session hashcat, pour pouvoir bruteforce une nouvelle fois le même hash avec l'état d'avancement du dernier bruteforce
