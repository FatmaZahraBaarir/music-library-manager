# TODO — Partie d’Enzo

> État vérifié le 6 novembre 2026 sur la branche `CLI_V1`.

L’exploration récursive, le filtrage par extension et type MIME ainsi que le modèle `Playlist` de base existent déjà. Il ne faut pas les refaire.

## Priorité 1 — Terminer la gestion XSPF

- [x] Créer un service XSPF dans `src/library/services/playlist/` (première version : playlist vide).
- [x] Transformer une liste de `Track` en playlist XSPF.
- [x] Générer automatiquement `default_playlist.xspf` après l’exploration d’un dossier.
- [x] Sauvegarder une playlist vers le chemin choisi par l’utilisateur.
- [x] Ouvrir un fichier `.xspf` existant.
- [x] Reconstituer un objet `Playlist` depuis le XML chargé.
- [x] Gérer correctement les chemins des morceaux sous forme d’URI.
- [x] Rejeter proprement :
  - [x] un fichier inexistant ;
  - [x] un fichier non-XSPF ;
  - [x] un XML invalide ;
  - [x] une playlist contenant des données incorrectes.
- [ ] Valider les fichiers générés avec <https://validator.xspf.org/>.
- [x] Ajouter les méthodes nécessaires dans `LibraryInterface` et `LibraryService`.
- [x] Écrire les tests automatiques de sauvegarde, d’ouverture et d’erreurs XSPF.

## Priorité 2 — Réaliser entièrement le CLI

Le parseur d’arguments existe ; les traitements de `-f`, `-d`, `-o` et `-p` restent à connecter aux services.

- [x] Créer le véritable point d’entrée `src/cli/main.py`.
- [x] Utiliser `argparse`.
- [x] Implémenter `-h` et `--help`.
- [x] Afficher une erreur utile lorsqu’aucun argument n’est fourni.
- [ ] Implémenter `-f FICHIER` :
  - [ ] vérifier le fichier ;
  - [ ] extraire ses métadonnées ;
  - [ ] les afficher clairement dans le terminal.
- [ ] Implémenter `-d DOSSIER` :
  - [ ] explorer récursivement le dossier ;
  - [ ] afficher les morceaux trouvés ;
  - [ ] construire la playlist par défaut.
- [x] Rendre `-f` et `-d` mutuellement exclusifs.
- [ ] Implémenter `-o FICHIER.xspf` avec `-d` pour choisir le fichier de sortie.
- [ ] Si `-o` est absent, utiliser `default_playlist.xspf`.
- [ ] Implémenter `-p FICHIER` en appelant le service de lecture audio réalisé par Fatma-Zahra.
- [ ] Gérer les chemins inexistants, les mauvais formats et les options incompatibles sans afficher de traceback brut.
- [ ] Tester les scénarios demandés dans le sujet :

```bash
python3 src/cli/main.py
python3 src/cli/main.py -h
python3 src/cli/main.py -d .
python3 src/cli/main.py -f music.mp3
python3 src/cli/main.py -d ./music/ -o playlist.xspf
python3 src/cli/main.py -p music.mp3
```

- [ ] Ajouter des tests automatiques pour chaque option CLI et chaque erreur importante.

## Priorité 3 — Faire la logique métier du drag & drop

Enzo fournit la logique de playlist exploitable par la GUI. La construction de l’affichage graphique appartient à Sanaa.

- [ ] Ajouter au modèle ou au service de playlist une opération pour ajouter un morceau.
- [ ] Ajouter une opération pour retirer un morceau.
- [ ] Conserver l’ordre d’ajout des morceaux.
- [ ] Décider et documenter si les doublons sont acceptés ; le modèle actuel les autorise.
- [ ] Vérifier qu’un fichier déposé est bien un MP3 ou FLAC valide.
- [ ] Permettre de créer une playlist personnalisée vide.
- [ ] Permettre de sauvegarder cette playlist en XSPF.
- [ ] Fournir à Sanaa des fonctions simples qu’elle pourra appeler depuis son drag & drop, sans placer la logique XML dans la GUI.
- [ ] Tester les ajouts, retraits, doublons, fichiers invalides et l’ordre des morceaux.

## Priorité 4 — Intégrer et vérifier la partie d’Enzo

- [ ] Brancher ensemble :
  - [ ] `FileService` ;
  - [ ] `LibraryService` ;
  - [ ] le futur service XSPF ;
  - [ ] le CLI ;
  - [ ] la logique de playlist.
- [ ] Ajouter les exports nécessaires dans les fichiers `__init__.py`.
- [ ] Vérifier que le CLI et la GUI utilisent les mêmes services métier.
- [ ] Fournir à Sanaa les fonctions exactes pour :
  - [ ] ouvrir une playlist ;
  - [ ] sauvegarder une playlist ;
  - [ ] ajouter ou retirer un morceau.
- [ ] Faire tester au moins un vrai MP3 et un vrai FLAC.
- [ ] Vérifier que le dépôt contient une déclaration des dépendances nécessaires, notamment `mutagen` et la bibliothèque fournissant `magic`.
- [ ] Relancer tous les tests dans l’environnement du projet.

## Blocage actuellement constaté

Les tests ne démarrent pas dans l’environnement Hermes parce que le module `magic` manque. Les cinq modules de tests échouent dès l’import. Cela ne prouve pas que le code est incorrect, mais la suite complète ne peut pas encore être validée dans cet environnement.

## Ordre de travail immédiat

1. [x] Service XSPF et ses tests.
2. [x] Sauvegarde de `default_playlist.xspf`.
3. [ ] Ouverture et validation XSPF.
4. [ ] CLI : `-f`, `-d`, `-o`, aide et erreurs.
5. [ ] Connexion de `-p` au lecteur audio de Fatma-Zahra.
6. [ ] Logique métier du drag & drop.
7. [ ] Intégration avec la GUI de Sanaa.
8. [ ] Tests complets sur de vrais fichiers.
