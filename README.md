# Music Library Manager

Projet de L3 Informatique réalisé en Python.

L'application permet de gérer une bibliothèque musicale composée de fichiers MP3 et FLAC. Elle doit fonctionner dans un terminal avec un CLI et avec une interface graphique.

## Membres du groupe

> Les noms complets et le numéro du groupe doivent être ajoutés avant le rendu final.

| Membre | Partie principale prévue |
|---|---|
| Enzo | Playlists XSPF, CLI et logique des playlists |
| Fatma-Zahra | Métadonnées et services externes |
| Sanaa | Interface graphique |

**Groupe de projet :** à compléter.

## Fonctionnalités actuellement disponibles

- exploration récursive d'un dossier ;
- détection des fichiers MP3 et FLAC par extension et type MIME ;
- lecture et modification des métadonnées ;
- création des objets `Track`, `Playlist`, `Metadata` et `Cover` ;
- sauvegarde d'une playlist au format XSPF ;
- ouverture d'une playlist XSPF ;
- récupération des morceaux MP3 et FLAC d'une playlist ;
- refus d'un fichier XSPF inexistant ;
- refus d'un fichier qui ne possède pas l'extension `.xspf` ;
- refus d'un fichier contenant un XML invalide ;
- refus d'un XML qui ne contient pas une playlist XSPF valide ;
- accès à la sauvegarde et à l'ouverture XSPF depuis `LibraryService` ;
- génération automatique de `default_playlist.xspf` depuis un dossier exploré ;
- première structure de l'interface graphique ;
- tests automatiques.

## Fonctionnalités encore en cours

- CLI complet avec les options demandées ;
- création automatique de `default_playlist.xspf` ;
- validation complète des fichiers XSPF ;
- ajout de morceaux par glisser-déposer ;
- branchement des boutons de l'interface graphique ;
- lecture audio ;
- récupération des informations d'album, des paroles et des pochettes.

## Dépendances

Le projet utilise :

- Python 3 ;
- `mutagen` pour les métadonnées MP3 et FLAC ;
- `python-magic` pour vérifier le type MIME des fichiers ;
- `tkinter` pour l'interface graphique ;
- `xml.etree.ElementTree`, fourni avec Python, pour créer et lire les fichiers XML/XSPF.

### Installation simple

Il est conseillé d'utiliser un environnement virtuel :

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install mutagen python-magic
```

Selon le système, `tkinter` et la bibliothèque système `libmagic` peuvent aussi être nécessaires.

## Lancer l'interface graphique

Depuis la racine du projet :

```bash
PYTHONPATH=src python3 src/gui/main.py
```

La structure de la fenêtre existe, mais ses boutons ne sont pas encore tous reliés aux services.

## Lancer le CLI

Le CLI est encore en cours de développement. La commande de lancement sera ajoutée ici lorsqu'il sera utilisable.

## Lancer les tests

### Tests des playlists XSPF

```bash
python3 src/tests-auto/playlist/test_xspf_service.py
```

Ces tests vérifient actuellement :

- la sauvegarde d'une playlist vide ;
- la sauvegarde d'une playlist avec un morceau ;
- l'ouverture d'une playlist vide ;
- la récupération d'un morceau MP3 ;
- le refus d'un fichier inexistant ;
- le refus d'un fichier non-XSPF ;
- le refus d'un XML invalide ;
- le refus d'un contenu qui n'est pas une playlist XSPF valide.
- la connexion entre `LibraryService` et `XspfService`.
- l'exploration d'un dossier suivie de la création de la playlist par défaut.

### Tous les tests

```bash
python3 -m unittest discover -s src/tests-auto -p "test_*.py" -v
```

Les tests utilisant de vrais fichiers audio demandent des fichiers locaux `sample.mp3` et `sample.flac` dans `src/tests-auto/fixtures/audio/`. Ces fichiers ne sont pas envoyés sur GitHub.

## Organisation du projet

```
music-library-manager/
├── src/
│   ├── library/       # Modèles et services
│   ├── cli/           # Interface en ligne de commande
│   ├── gui/           # Interface graphique
│   └── tests-auto/    # Tests automatiques
├── doc/               # Documents du projet
└── README.md
```

## Gestion des playlists XSPF

Le service `XspfService` se trouve dans :

```
src/library/services/playlist/xspf_service.py
```

Il permet de :

- sauvegarder une `Playlist` dans un fichier `.xspf` ;
- enregistrer les chemins des morceaux au format `file:///...` ;
- ouvrir un fichier `.xspf` ;
- recréer les objets `Track` correspondant aux morceaux.

## État du projet

Le projet est en cours de développement. Ce README doit être mis à jour après chaque fonctionnalité importante afin que les commandes et la répartition du travail restent correctes.
