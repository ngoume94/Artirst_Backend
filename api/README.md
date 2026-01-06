# Mission : **Construire un Écosystème Data Centré sur Data Musical avec Python, FastAPI et Streamlit** 

**Contexte : Plongez dans l’univers de l'industrie musicale et de la Data Science**


Imaginez une entreprise fictive, **SoundStream Analytics**, qui souhaite révolutionner la compréhension des tendances musicales grâce à une plateforme intelligente exploitant les données de musiques. Leur ambition ? **Créer un système ultra-performant d'analyse du comportement des auditeurs** à destination des labels discographiques, des curateurs de playlists et des plateformes de streaming.  

Mais il y a un problème... **Leurs données sont dans un état chaotique !** 
Les informations sur les artistes sont incomplètes, les habitudes d'écoute des utilisateurs sont éparpillées et les relations sociales entre fans sont inexploitables. Aucun système centralisé ne permet de requêter efficacement les informations sur l'intensité d'écoute d'un artiste (weight), les tags associés par la communauté ou les recommandations basées sur les profils similaires.


C'est là **que vous entrez en jeu**, en tant que **Consultant Data & Architecte API** ! Votre mission ? Transformer ce chaos en un écosystème data structuré, fluide et performant. Vous serez **le chef d’orchestre** de ce projet, portant successivement trois casquettes :


---

## **Phase 1 : Développeur Python & Architecte API**  

![](architecture.png)

**Objectif : Construire une API robuste pour centraliser et exposer les données Last.fm.**  

🔹 **Design de la base de données** :  
- Modéliser la base de données en SQL à partir des fichiers .dat.  
- Utiliser **SQLite** pour stocker les données de manière efficace.  
- Gérer les relations **Many-to-Many** sophistiquées : les écoutes d'artistes par les utilisateurs, les marquages par tags et le graphe social d'amitié.  

🔹 **Développement de l’API avec FastAPI** :  
- Concevoir un **API RESTful** permettant d'interroger facilement le catalogue musical et les comportements utilisateurs.  
- Intégrer **Pydantic** pour une validation stricte et un typage fort des données entrantes et sortantes.  
- Utiliser **SQLAlchemy** pour la gestion des requêtes à la base de données.  
- Implémenter une logique métier avancée : recherche multicritères par tags, statistiques globales et moteur de recommandation collaborative.

🔹 **Qualité et Tests** :

- Développer une suite de **tests automatisés** pour valider chaque endpoint (CRUD, Health Check, Analytics).
- Assurer la robustesse des endpoints face aux erreurs (gestion des 404, validation des formats).
- Générer une documentation interactive automatique via **Swagger**.

🔹 **Déploiement de l’API** :  
- Héberger l’API sur un cloud public (**Render, AWS, Azure, GCP**).  
- Conteneuriser l'application avec **Docker** pour garantir un déploiement "on-premise" ou Cloud sans friction.  
- Sécuriser les endpoints et optimiser les performances.  

🔹 **Création d’un SDK en Python** :  
- Développer un **package Python** permettant aux utilisateurs d'interagir facilement avec l’API.  
- Publier ce package sur **PyPI**, afin qu’il puisse être utilisé dans d'autres projets.  

**Livrables** :  
- Une base de données centralisée et prête à l’emploi.  
- Une API FastAPI documentée et déployée.  
- Un SDK Python simple d'utilisation et bien documenté
- Un script de test complet garantissant la fiabilité de l'écosystème.

---

## **Phase 2 : Data Analyst - Exploration et Visualisation**  

![](architecturephase.png)

**Objectif : Explorer les comportements d'écoute et visualiser les tendances musicales en interrogeant l’API.**  

🔹 **Analyse Exploratoire des Données (EDA)** :  
- Utiliser le **SDK Python** pour requêter l’API et récupérer les données.  
- Analyser la distribution des poids d'écoute (weight) pour identifier les artistes "superstars" vs la "longue traîne".  
- Étudier les genres les plus populaires et les préférences des utilisateurs.  

🔹 **Construction d’une Data App avec Streamlit** :  
- Créer une **application interactive** qui permet de visualiser les tendances du cinéma.    
- Étudier la structure du **graphe social** : corrélation entre le nombre d'amis et la diversité des artistes écoutés.
- Mapper les **nuages de tags** pour identifier les genres dominants et les niches musicales.

🔹 **Construction d’une Data App avec Streamlit** :

Développer une **application interactive** qui se connecte en temps réel à votre API FastAPI.

Créer un **Dashboard de Recommandation** : l'utilisateur saisit son ID et l'app affiche visuellement les artistes suggérés par votre algorithme.

Intégrer des **visualisations dynamiques** : top 10 des artistes les plus écoutés, répartition géographique ou temporelle des tags.

Offrir un **moteur de recherche granulaire** permettant de filtrer les artistes par combinaisons de tags et popularité.

**Livrables** :  
- Un **Notebook Python** détaillant l'analyse statistique des habitudes d'écoute.  
- Une **application web Streamlit** connectée à l'écosystème, transformant les données brutes de l'API en insights stratégiques pour les curateurs musicaux.

---

## **Pourquoi cette mission est incontournable pour tout Consultant Data ?**  

- **Expérience complète et immersive** : Vous touchez **à toutes les facettes** d’un projet Data moderne, de la structuration SQL à la recommandation intelligente.  
- **Projet concret et impactant** : Qui n'a jamais rêvé d'un système capable de cartographier les goûts musicaux et de prédire le prochain coup de cœur d'un auditeur ?  
- **Compétences ultra-prisées** : Vous manipulez **FastAPI, SQLAlchemy, Streamlit, Machine Learning, Cloud, et Docker**.  
- **Un atout pour votre portfolio** : À la fin, vous aurez un projet **clé en main**, à exhiber fièrement sur GitHub ou en démo pour vos futurs clients.  

- **Prêt à relever le défi et à devenir un Développeur d'API et Data analyst ?** Rejoignez le cours dès maintenant et embarquez pour une aventure 100% immersive dans le monde fascinant des données musicales ! 

---

**BONUS** :  
- Accès au **code source** complet (Backend FastAPI + Tests automatisés).  

---

# Dataset MovieLens - Description des Données

Le dataset utilisé dans ce projet est un ensemble de données riche et multidimensionnel inspiré de la plateforme Last.fm. Il permet de modéliser non seulement les catalogues musicaux, mais aussi les comportements sociaux et les préférences subjectives. Ce dataset est le terrain de jeu idéal pour construire des systèmes de recommandation collaboratifs et des API capables de gérer des relations complexes à grande échelle.

## Fichiers et Structure des Données

### 1. artists.dat
Contient la liste des artistes musicaux avec leurs métadonnées de base.

**Colonnes :**
- `id` : Identifiant unique de l'artiste (clé primaire).
- `name` : Nom officiel de l'artiste ou du groupe.
- `url` : Lien vers la page de l'artiste sur le site Last.fm.
- `pictureURL` : URL de l'image ou de l'avatar de l'artiste.

**Exemple :**
```
id,name,url,pictureURL
1,MALICE MIZER,http://www.last.fm/music/MALICE+MIZER,http://userserve-ak.last.fm/serve/252/1083.jpg
2,Diary of Dreams,http://www.last.fm/music/Diary+of+Dreams,http://userserve-ak.last.fm/serve/252/3052066.jpg
```

---

### user_artists.dat
Contient les statistiques d'écoute des utilisateurs. C'est le cœur de l'analyse comportementale.

**Colonnes :**
- `userID` : Identifiant unique de l'utilisateur (clé étrangère vers `User`).
- `artistID` : Identifiant de l'artiste écouté (clé étrangère vers `Artist`).
- `weight` : Poids de l'écoute, représentant le nombre total de lectures (plays) effectuées par cet utilisateur pour cet artiste.

**Exemple :**
```
userID,artistID,weight
2,51,13883
4,52,11690
```

---

### 3. user_taggedartists.dat
Contient les étiquettes (tags) appliquées par les utilisateurs aux artistes pour les catégoriser.

**Colonnes :**
- `userID` : Identifiant de l'utilisateur ayant posé le tag.
- `artistID` : Identifiant de l'artiste concerné.
- `tagID` : Identifiant du tag (référence vers la table Tag).
- `timestamp` : Horodatage UNIX du moment où l'artiste a été tagué.

**Exemple :**
```
userID,artistID,tagID,timestamp
2,52,13,1235396034
2,52,15,1235396034
```

---

### 4. user_friends.dat
Contient le graphe social de la plateforme, indispensable pour les recommandations collaboratives.

**Colonnes :**
- `userID` : Identifiant de l'utilisateur.
- `friendID` : Identifiant de l'utilisateur ami.
**Note** : Dans votre application, cette relation est bidirectionnelle et permet de construire des cercles d'influence musicale.

**Exemple :**
```
userID,friendID
2,275
2,428
```

---
### 5. tags.dat
Table de référence contenant la valeur textuelle des identifiants de tags utilisés.

**Colonnes :**
- `tagID` : Identifiant unique du tag.
- `tagValue` : Libellé du tag (ex: "rock", "80s", "female vocalists").

**Exemple :**
```
tagID,tagValue
13,chillout
15,ambient
```

---

## Structure de la Base de Données SQLite3

Pour orchestrer cet écosystème musical, nous avons défini le schéma relationnel suivant :

### Table `artists`
```sql
CREATE TABLE artists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT,
    pictureURL TEXT
);
```

### Table `users`
```sql
CREATE TABLE users (
    userID INTEGER PRIMARY KEY
);
```

### Table `user_artists`
```sql
CREATE TABLE user_artists (
    userID INTEGER,
    artistID INTEGER,
    weight INTEGER NOT NULL,
    PRIMARY KEY (userID, artistID),
    FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE,
    FOREIGN KEY (artistID) REFERENCES artists(id) ON DELETE CASCADE
);
```

### Table `tags`
```sql
CREATE TABLE tags (
    tagID INTEGER PRIMARY KEY AUTOINCREMENT,
    tagValue TEXT NOT NULL UNIQUE
);
```

### Table `user_taggedartists`
```sql
CREATE TABLE user_taggedartists (
    userID INTEGER,
    artistID INTEGER,
    tagID INTEGER,
    timestamp INTEGER NOT NULL,
    day INTEGER,
    month INTEGER,
    year INTEGER,
    PRIMARY KEY (userID, artistID, tagID, timestamp),
    FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE,
    FOREIGN KEY (artistID) REFERENCES artists(id) ON DELETE CASCADE,
    FOREIGN KEY (tagID) REFERENCES tags(tagID) ON DELETE CASCADE
);
```

### Table `user_friends`
```sql
CREATE TABLE user_friends (
    userID INTEGER,
    friendID INTEGER,
    PRIMARY KEY (userID, friendID),
    FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE,
    FOREIGN KEY (friendID) REFERENCES users(userID) ON DELETE CASCADE
);
```

## Relations entre les Tables
- **Clés Étrangères** : Les tables `user_artists`, `user_taggedartists` et `user_friends` servent de ponts relationnels. Elles assurent que chaque interaction (écoute, tag ou amitié) est rattachée à des entités existantes.
- **Intégrité Référentielle** : L'utilisation de `ON DELETE CASCADE` garantit que si un artiste ou un utilisateur est supprimé, toutes ses interactions liées sont automatiquement nettoyées, évitant ainsi les données orphelines.
- **Clés Composites** : Pour les écoutes et les amitiés, nous utilisons des clés primaires composites (ex: `userID + artistID`) pour garantir l'unicité des relations et optimiser les performances de recherche.

Cette architecture transforme des fichiers plats en un graphe de données interconnecté, idéal pour alimenter vos algorithmes de recommandation et vos tableaux de bord analytiques.


# Création de la Base de Données SQLite3 et de ses tables

```bash
(.venv) vant@MOOVE15:~/D:/End_To_End_Data_Science_Project/Artirst_Backend$ sqlite artist.db
```

```sql
CREATE TABLE artists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT,
    pictureURL TEXT
);
```

```sql
CREATE TABLE users (
    userID INTEGER PRIMARY KEY
);
```

```sql
CREATE TABLE user_artists (
    userID INTEGER,
    artistID INTEGER,
    weight INTEGER NOT NULL,
    PRIMARY KEY (userID, artistID),
    FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE,
    FOREIGN KEY (artistID) REFERENCES artists(id) ON DELETE CASCADE
);
```

```sql
CREATE TABLE tags (
    tagID INTEGER PRIMARY KEY AUTOINCREMENT,
    tagValue TEXT NOT NULL UNIQUE
);
```

```sql
CREATE TABLE user_taggedartists (
    userID INTEGER,
    artistID INTEGER,
    tagID INTEGER,
    timestamp INTEGER NOT NULL,
    day INTEGER,
    month INTEGER,
    year INTEGER,
    PRIMARY KEY (userID, artistID, tagID, timestamp),
    FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE,
    FOREIGN KEY (artistID) REFERENCES artists(id) ON DELETE CASCADE,
    FOREIGN KEY (tagID) REFERENCES tags(tagID) ON DELETE CASCADE
);
```

```sql
CREATE TABLE user_friends (
    userID INTEGER,
    friendID INTEGER,
    PRIMARY KEY (userID, friendID),
    FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE,
    FOREIGN KEY (friendID) REFERENCES users(userID) ON DELETE CASCADE
);
```

# Chargement des Données dans les Tables SQLite3

## Activation des clés étrangères

```sql
PRAGMA foreign_keys = ON;
```

La commande **`PRAGMA foreign_keys = ON;`** dans SQLite sert à **activer les clés étrangères**.  Cela garantit que toutes les contraintes de clés étrangères seront respectées.

### **Explication** :

- SQLite **ne vérifie pas** les contraintes de clé étrangère par défaut.
- Cette commande **active** l'intégrité référentielle, ce qui signifie que :
  - Une valeur de clé étrangère doit correspondre à une clé primaire existante.
  - Si une ligne référencée est supprimée ou modifiée, cela peut entraîner une erreur ou déclencher une action définie (ex: `ON DELETE CASCADE`).

### **Bonnes pratiques** :

- Toujours activer les clés étrangères en début de session SQLite :
  ```sql
  PRAGMA foreign_keys = ON;
  ```
- Pour vérifier si les clés étrangères sont activées :
  ```sql
  PRAGMA foreign_keys;
  ```
  - Retourne `1` si activé, `0` sinon.


## Préparez l'instruction d'importation pour reconnaître le format CSV avec la commande suivante :

```sql
.separator "\t"
```

## Chargement des données des fichiers csv dans les tables

### Chargement

```sql
.import --skip 1 Data/artists.dat artists
```

```sql
.import --skip 1 Data/user_artists.dat user_artists
```

```sql
.import --skip 1 Data/tags.dat tags
```

```sql
.import --skip 1 Data/user_taggedartists.dat user_taggedartists
```

```sql
.import --skip 1 Data/user_friends.dat user_friends
```

### **Vérifions que les données ont été chargées** :

```sql
SELECT * FROM artists LIMIT 2;
```

```
1,"MALICE MIZER","http://www.last.fm/music/MALICE+MIZER","http://images.last.fm/1083.jpg"
2,"Diary of Dreams","http://www.last.fm/music/Diary+of+Dreams","http://images.last.fm/30520.jpg"
```

```sql
SELECT COUNT(*) AS total_artists FROM artists;
```

```
2101
```

```sql
SELECT COUNT(*) AS total_listens FROM user_artists;
```

```
92834
```

```sql
SELECT userID, artistID, weight FROM user_artists LIMIT 3;
```

```
2,51,13883
2,52,11690
2,53,11351
```

Pour quitter l'interface en lignes de commandes de SQLite, tapez cette commande :

```sql
.exit
```