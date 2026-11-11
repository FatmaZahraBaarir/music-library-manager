# Tests automatiques

Les tests sont classés par domaine fonctionnel.

```text
tests-auto/
├── audio/       # lecteur, service audio et délégation par LibraryService
├── cli_tests/   # arguments, fichiers, dossiers et lecture audio du CLI
├── file/        # exploration récursive et filtrage des fichiers
├── library_tests/ # façade commune LibraryService
├── metadata/    # conversion, lecture et écriture des métadonnées
├── playlist/    # modèle de playlist, service XSPF et façade
└── fixtures/
    └── audio/   # petits fichiers MP3 et FLAC utilisés par les tests réels
```

## Lancer toute la suite

Depuis la racine du projet :

```bash
PYTHONDONTWRITEBYTECODE=1 PYGAME_HIDE_SUPPORT_PROMPT=1 SDL_AUDIODRIVER=dummy \
python3 -B -m unittest discover -s src/tests-auto -p "test_*.py" -v
```

Le pilote audio factice évite de produire du son pendant les tests.

## Lancer un domaine particulier

Exemple pour les métadonnées :

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover \
-s src/tests-auto/metadata -p "test_*.py" -v
```

Remplacer `metadata` par `audio`, `cli_tests`, `file`, `library_tests` ou `playlist` selon le domaine à vérifier.

## Fichiers audio de référence

Les fixtures canoniques sont :

```text
fixtures/audio/sample.mp3
fixtures/audio/sample.flac
```

Les tests qui modifient les tags utilisent toujours des copies temporaires et ne modifient jamais ces fichiers originaux.
