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
- affichage et modification des métadonnées d'un fichier MP3 ou FLAC avec l'option CLI `-f` ;
- lecture d'un fichier MP3 ou FLAC avec l'option CLI `-p` ;
- création d'une playlist vide, ajout et retrait de morceaux ;
- lecture audio des morceaux MP3 et FLAC via `AudioService` ;
- pause, reprise et arrêt de la lecture ;
- progression ordonnée d'une playlist via le thread principal du CLI ou de la GUI ;
- première structure de l'interface graphique ;
- tests automatiques.

## Fonctionnalités encore en cours

- CLI complet avec les options demandées ;
- validation complète des fichiers XSPF ;
- ajout de morceaux par glisser-déposer ;
- branchement des boutons de l'interface graphique ;
- branchement de la lecture audio au CLI et à la GUI ;
- récupération des informations d'album, des paroles et des pochettes.

## Dépendances

Le projet utilise :

- Python 3 ;
- `mutagen` pour les métadonnées MP3 et FLAC ;
- `python-magic` pour vérifier le type MIME des fichiers ;
- `pygame-ce` pour lire, mettre en pause et arrêter les fichiers audio ;
- `tkinter` pour l'interface graphique ;
- `xml.etree.ElementTree`, fourni avec Python, pour créer et lire les fichiers XML/XSPF.

### Installation simple

Il est conseillé d'utiliser un environnement virtuel :

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Sur macOS avec Homebrew, la bibliothèque système utilisée par `python-magic` s'installe avec :

```bash
brew install libmagic
```

Si Python ne trouve pas cette bibliothèque, ajouter son dossier avant l'exécution :

```bash
export DYLD_LIBRARY_PATH="/opt/homebrew/opt/libmagic/lib"
```

Selon le système, `tkinter` peut aussi être nécessaire.

## Lancer l'interface graphique

Depuis la racine du projet :

```bash
PYTHONPATH=src python3 src/gui/main.py
```

La structure de la fenêtre existe, mais ses boutons ne sont pas encore tous reliés aux services.

## Lancer le CLI

Le CLI lit ou modifie les métadonnées d'un fichier et crée une playlist depuis un dossier :

```bash
python3 src/cli/main.py -h
python3 src/cli/main.py -f ./music/song.mp3
python3 src/cli/main.py -f ./music/song.mp3 --title "Nouveau titre" --artist "Nouvel artiste"
python3 src/cli/main.py -f ./music/song.flac --album "Nouvel album" --track-number 3 --year 2026
python3 src/cli/main.py -p ./music/song.mp3
python3 src/cli/main.py -d ./music/
python3 src/cli/main.py -d ./music/ -o playlist.xspf
```

Les champs modifiables sont `--title`, `--artist`, `--album`, `--track-number` et `--year`. Les champs absents restent inchangés. L'option `-p` lit le fichier jusqu'à sa fin ; `Ctrl+C` arrête proprement la lecture.

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

### Tests des arguments du CLI

```bash
python3 -m unittest discover -s src/tests-auto/cli -p "test_*.py" -v
```

### Tous les tests

```bash
PYTHONDONTWRITEBYTECODE=1 PYGAME_HIDE_SUPPORT_PROMPT=1 SDL_AUDIODRIVER=dummy \
python3 -B -m unittest discover -s src/tests-auto -p "test_*.py" -v
```

La commande unique découvre les tests classés dans `audio`, `cli_tests`, `file`, `library_tests`, `metadata` et `playlist`.

Deux fichiers audio de test sont disponibles dans `src/tests-auto/fixtures/audio/` : `sample.mp3` et `sample.flac`. Ils servent à tester les formats MP3 et FLAC ainsi que la lecture et la modification des métadonnées.

## Organisation du projet

```
music-library-manager/
├── src/
│   ├── library/       # Modèles et services
│   ├── cli/           # Interface en ligne de commande
│   ├── gui/           # Interface graphique
│   └── tests-auto/    # Tests automatiques
├── doc/               # Documents du projet
├── requirements.txt   # Dépendances Python
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

## Gestion des playlists personnalisées

`LibraryService` fournit trois méthodes utilisables par l'interface graphique :

- `create_empty_playlist` pour créer une playlist vide ;
- `add_track_to_playlist` pour vérifier puis ajouter un MP3 ou un FLAC ;
- `remove_track_from_playlist` pour retirer un morceau selon sa position.

L'ordre d'ajout est conservé et les doublons sont autorisés.

## État du projet

Le projet est en cours de développement. Ce README doit être mis à jour après chaque fonctionnalité importante afin que les commandes et la répartition du travail restent correctes.
