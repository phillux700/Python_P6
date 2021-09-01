![Python 3.8](https://img.shields.io/badge/python-3.8%2B-green)

# Règle de sauvegarde 3-2-1

## Description
Ce projet, sous python 3.8, a pour but de sauvegarder un site wordpress et sa base de données en suivant la règle 3-2-1.
* Disposer de **3** copies de sauvegarde.
* Stocker les copies sur **2** supports différents.
* Conserver **une** copie de la sauvegarde hors site.

## Installation 
***Clonage du projet:***   
```
git clone https://github.com/sergisergio/P6.git  
```
***Identifiants***

Faire une copie du fichier config.py.dist sous le nom config.py et entrez vos identifiants.
* identifiants FTP
* identifiants IAM AWS
* nom du bucket S3
```
cp config.py.dist config.py
```

![Config](https://github.com/sergisergio/P6/blob/main/images/config.png?raw=true)

***Packages***

Vérifiez l'installation des packages config ainsi que ceux dans le fichier 'requirements.txt'

## Usage

```bash
python3 main.py
```
![Menu](https://github.com/sergisergio/P6/blob/main/images/menu.png?raw=true)

## Topologie

**Topologie** de test sur **GNS3**:

![GNS3](https://github.com/sergisergio/P6/blob/main/images/topo.png?raw=true)

## Résumé

* 1. Sauvegarde sur serveur local et rotation
* 2. Sauvegarde sur serveur distant et rotation
* 3. Sauvegarde sur AWS (rotation automatique via la console AWS)
* 4. Les 3 précédentes en simultané
* 5. Restauration à partir d'une sauvegarde du site local
* 6. Restauration à partir d'une sauvegarde du site distant
* 7. Restauration à partir d'une sauvegarde du bucket S3 d'AWS    
    
NB: Pour les restaurations, une liste apparaît: il vous suffira de choisir quelle sauvegarde vous souhaitez.
 
![List](https://github.com/sergisergio/P6/blob/main/images/list.png?raw=true)

## Licence
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)