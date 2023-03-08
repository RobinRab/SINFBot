# 💡 À propos
Ce dépôt contient le code source du bot Anon, du serveur discord Sinf Illégal Family. Tout le monde peut participer à son développement.



# 📖 Dépendances
Pour faire fonctionner le code du bot vous allez avoir besoin d'installer plusieurs dépendances 

## 1. python3.11
Le bot discord qui tourne en permanence demande de nombreuses ressources, il tourne donc sur la dernière version de python (3.11) car elle est plus rapide de 60% et permet l'utilisation de plus d'outils

## 2. git
Pour ce projet git vous aurez besoin d'installer git sur votre machine, ça vous permettra de clone le projet ainsi que d'y apporter des modifications

## 3. dotenv
Le module dotenv permet de lire un fichier `.env` dans votre dépôt, celui-ci sera nécessaire plus tard

# 🛠️ Setup des tests
## 1. créer votre bot de test
> ### 1. Connectez vous à discord et rendez-vous sur [Discord Developper Portal](https://discord.com/developers/applications)
> ### 2. Cliquez sur "New Application"
> ### 3. Donnez lui un nom et appuyez sur "create"
> ### 4. Allez dans l'onglet 'Bot' et cliquez sur "Add bot" 
> ### 5. Désactivez "Public bot"
> ### 6. Activez les 3 checks intents 
> ### 7. rejoingnez le serveur de [testing](https://discord.gg/5braTFUa8h)
> ### 8. Dans le portal, allez dans Oauth2/URL GENERATOR, sélectionnez 'bot' puis 'administator' et copiez le lien
Vous voici désormais prêt avec votre bot pour tous les tests, ceci est nécessaire par sécurité pour le serveur principal ainsi que pour éviter les spams que certains tests peuvent provoquer. <br> Sur votre compte discord, je vous conseille d'aller dans settings/Advanced et d'activer le mode développeur, cela vous permettra de copier l'ID de vos messages, serveurs, etc.

## 2. forker le projet
Pour forker le projet, cliquez sur le bouton "fork" en haut à droite de la page, vous aurez alors une copie du projet sur votre compte github. <br> Vous pouvez maintenant cloner le projet sur votre machine via git et le modifier comme ci-dessous

## 3. créer le fichier `.env`
Dans le dossier principal, créer un fichier `.env` contenant toutes vos variables personnelles, celles-ci ne seront pas partagées avec les autres développeurs. <br> Le fichier `.env` doit contenir les variables suivantes:
```py
BOT_PREFIX = "!"
DISCORD_API_TOKEN = "your secret token here"

BOT_ID = int
GUILD_ID = 1079214079161417879
ERROR_CHANNEL_ID = 1079217228081283122

ANON_SAYS_ID = 1079223122592550982
GENERAL_ID = 1079214079161417882
CONFESSION_ID = 1079217281449590836
CUTIE_ID = 1079337720041705472
```