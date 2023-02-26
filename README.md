<h1 align="center">
	📖 Anon
</h1>

<p align="center">
	<b><i>Un bot parfait sans aucun bug</i></b><br>
</p>

<p align="center">
	<img alt="GitHub code size in bytes" src="https://img.shields.io/github/languages/code-size/RobinRab/SINF-Bot?color=lightblue" />
	<img alt="Number of lines of code" src="https://img.shields.io/tokei/lines/github/RobinRab/SINF-Bot?color=critical" />
	<img alt="Code language count" src="https://img.shields.io/github/languages/count/RobinRab/SINF-Bot?color=yellow" />
	<img alt="GitHub top language" src="https://img.shields.io/github/languages/top/RobinRab/SINF-Bot?color=blue" />
	<img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/RobinRab/SINF-Bot?color=green" />
</p>

<h3 align="center">
	<a href="💡 À propos">À propos</a>
	<span> · </span>
	<a href="📖 Dépendances">Dépendances</a>
	<span> · </span>
	<a href="#🛠️ Setup">Setup</a>
</h3>


# 💡 À propos
Ce dépôt contient le code source du bot Anon, du serveur discord Sinf Illégal Family. Tout le monde peut participer à son développement.



# 📖 Dépendances
Pour faire fonctionner le code du bot vous allez avoir besoin d'installer plusieurs dépendances 

## 1. python3.11
Le bot discord qui tourne en permanence demande de nombreuses ressources, il tourne donc sur la dernière version de python (3.11) car elle est plus rapide de 60% et permet l'utilisation de plus d'outils

## 2. git
Pour ce projet git vous aurez besoin d'installer git sur votre machine, ça vous permettre dans clone le projet ainsi que d'y apporter des modifications

## 3. dotenv
Le module dotenv permet de lire un fichier `.env` dans votre dépôt, celui-ci sera nécessaire plus tard

# 🛠️ Setup le bot

## 1. créer votre bot de test
> ### 1. Connectez vous à discord et rendez-vous sur [Discord Developper Portal](https://discord.com/developers/applications)
> ### 2. Cliquez sur "New Application"
> ### 3. Donnez lui un nom et appuyez sur "create"
> ### 4. Allez dans l'onglet 'Bot' et cliquez sur "Add bot" 
> ### 5. Activez les 3 checks intents 
> ### 6. Copiez le token de votre bot via le bouton "copy token"
> ### 7. rejoingnez le serveur de [testing](https://discord.gg/5braTFUa8h)
> ### 8. Invitez votre bot dessus via [ce lien](https://discord.com/oauth2/authorize?response_type=code&client_id=CLIENT_ID&scope=bot+applications.commands&permissions=8&guild_id=1078948017773756496), remplacez CLIENT_ID dans l'url par l'ID que vous trouverez dans "General Information" du portal
Vous voici désormais prêt avec votre bot pour tous les tests, ceci est nécessaire par sécurité pour le serveur principal ainsi que pour éviter les spams que certains tests peuvent provoquer. <br> Sur votre compte discord, je vous conseille d'aller dans settings/Advanced et d'activer le mode développeur, cela vous permettra de copier l'ID de vos messages, serveurs, etc.

## 2. cloner le projet
```
git clone https://github.com/RobinRab/SINF-Bot
```

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
```
**BOT_PREFIX** est le préfixe que vous voulez donner à votre bot, par exemple `!` ou `?` <br>
**DISCORD_API_TOKEN** est le token que vous avez copié plus tôt <br> 
**BOT_ID** est l'ID de votre bot, vous pouvez le trouver dans "General Information" du portal <br>
Les autres ID correspondent déjà à ceux sur le serveur de test, vous pouvez les laisser tels quels

## 4. Lancer le bot 🚀
```py
python3.11 main.py
```
Le bot devrait maintenant être en ligne, vous pouvez le tester comme vous le souhaitez. Pour l'arrêter, appuyez sur `CTRL + C` dans le terminal

# 📡 Partager vos modifications

ça je sais pas encore comment faire, mais je pense que chacun aura le droit de créer sa branche te la modifier en ajouter un dossier à son nom avec ses fonctions, ensuite il pourra proposer de merge, on check le code et il est ajouté au main si tout est bon

ATTENTION: ne pas oublier que je sais pas quoi faire avec le fichier `json` entre chaque branche


# 📝 Comment ça marche?
## `Main.py`
Le fichier `main.py` est le fichier principal, c'est lui qui va lancer le bot et qui va importer les commandes qui se trouvent sous forme d'extensions 
```py
bot = commands.Bot( 
	command_prefix=[settings.BOT_PREFIX, f"<@!{settings.BOT_ID}> "],
	case_insensitive=True,
	help_command=None,
	intents=intents,
	strip_after_prefix=True
)
bot.tree.synced : bool = False
```
créer l'objet bot, il est aussi possible de lui ajouter des attributs comme `bot.tree.synced` qui est un booléen qui permet de savoir si l'arbre a été synchronisé ou non

```py
@bot.event
async def on_ready():
	for ext in settings.extensions:
		await bot.load_extension(ext)
		print(...)
		log("INFO", f"{ext} loaded ")
```
Lorsque le bot est prêt, il va charger toutes les extensions qui se trouvent dans le fichier `settings.py`

## `settings.py`
Le fichier `settings.py` contient toutes les variables globales du projet, il défini les variables, les routes, les extensions ainsi que un logger pour garder une trace des erreurs. C'est un fichier senssible, il ne devrait pas être modifé excepté en cas d'ajout de fonctionnalités

## `utils.py`
Le fichier `utils.py` contient toutes les fonctions utiles au projet, si vous voulez ajouter une fonction qui se retrouve souvent nécessaire, il faut la mettre dans ce fichier

## `.gitignore`
Le fichier `.gitignore` permet d'ignorer certains fichiers lors de l'upload sur github, il est important de ne modifier que si nécessaire

## `cmds/`
Le dossier `cmds/` contient tous les fichiers qui contiennent les commandes du bot, il est important de respecter leur structure. <br>
Chaque dossier dans `cmds/` correspond à une catégorie de commandes, par exemple `cmds/cutie/` contient toutes les commandes qui concernent les cuties. <br>
Pour vos commandes, je vous encourage à créer un dossier à votre nom dans lequels vous pourrez ajouter vos fichiers 

---

## Vous trouverez plus d'informations sur le code en lisant la [documentation](https://discordpy.readthedocs.io/en/stable/)
--- 
