# Conclusion du point d’avancement

## Bilan général

À la date du point d’avancement du 13 novembre 2026, le projet dispose d’un socle fonctionnel commun au CLI et à la GUI. L’application sait explorer une arborescence, reconnaître les fichiers MP3 et FLAC, lire et modifier leurs métadonnées, créer et ouvrir des playlists XSPF et lire des fichiers audio. Une première version de l’interface graphique et une suite de tests automatiques sont également disponibles.

Le travail réalisé correspond aux fonctionnalités prioritaires prévues dans le diagramme de Gantt. Les pourcentages d’avancement restent cependant à valider collectivement par les trois membres du groupe.

## Difficultés surmontées

### Vérification des fichiers audio

La première difficulté a été de ne pas accepter un fichier uniquement à partir de son extension. Un fichier portant le suffixe `.mp3` ou `.flac` peut contenir autre chose qu’un flux audio valide.

Cette difficulté a été traitée en combinant :

- la vérification de l’extension avec `pathlib` ;
- la vérification du type MIME avec `python-magic` ;
- le rejet des fichiers dont l’extension et le type réel ne correspondent pas.

Des faux fichiers MP3 et FLAC ont été ajoutés au jeu de démonstration pour vérifier ce comportement.

### Gestion de deux formats de métadonnées

Les MP3 utilisent des tags ID3 alors que les FLAC utilisent des commentaires Vorbis. Les noms et les méthodes d’écriture ne sont donc pas identiques.

Une représentation commune a été mise en place avec les classes `Track` et `Metadata`. Les opérations propres à chaque format sont séparées dans `MetadataReader` et `MetadataWriter`, tandis que `MetadataService` choisit le traitement adapté.

La valeur `None` signifie qu’un champ ne doit pas être modifié, afin d’éviter l’effacement involontaire d’une métadonnée existante.

### Séparation entre les services, le CLI et la GUI

Il fallait éviter que le CLI et la GUI utilisent directement tous les services techniques. Une façade commune a donc été créée avec `LibraryInterface` et `LibraryService`.

Cette organisation permet :

- de centraliser les fonctionnalités métier ;
- de réutiliser le même traitement dans le CLI et la GUI ;
- d’éviter les affichages directs dans les services ;
- de faciliter les tests avec de faux services.

### Création et ouverture des playlists XSPF

La création des fichiers XSPF a demandé de gérer correctement :

- le namespace XML du format XSPF ;
- les chemins sous la forme d’URI `file:///...` ;
- l’encodage des espaces avec `%20` ;
- l’ouverture et la reconstruction des objets `Track` ;
- le rejet des fichiers inexistants ou des XML invalides ;
- l’indentation du XML pour obtenir un fichier lisible.

### Lecture audio et enchaînement des morceaux

La lecture audio devait fonctionner avec les MP3 et les FLAC tout en restant compatible avec le CLI et la boucle d’événements de Tkinter.

Le projet utilise `pygame-ce`. La première architecture envisagée utilisait un thread secondaire et un verrou. Elle a finalement été simplifiée : le CLI ou la GUI appelle périodiquement `update_playlist_playback()` depuis son thread principal. Cette solution est plus facile à comprendre, à expliquer et à intégrer à Tkinter.

### Compatibilité des commandes de lancement

Les imports des packages `gui` et `library` ne fonctionnaient pas toujours lorsque les fichiers étaient exécutés directement. Les points d’entrée ont été adaptés afin de permettre les commandes demandées, notamment :

```bash
python3 src/gui/main.py
python3 src/cli/main.py -h
```

### Tests sans modifier les fichiers originaux

Les tests de modification des métadonnées risquaient d’altérer définitivement les morceaux utilisés comme références. Les tests d’écriture travaillent maintenant sur des copies temporaires. Les fichiers originaux `sample.mp3` et `sample.flac` restent donc stables.

## Fonctionnalités réalisées

Les éléments suivants sont disponibles au moment du point d’avancement :

- exploration récursive d’un dossier et de ses sous-dossiers ;
- filtrage par extension et type MIME ;
- lecture des métadonnées MP3 et FLAC ;
- modification et sauvegarde des tags ID3 et des commentaires Vorbis ;
- récupération de la durée d’un morceau ;
- représentation commune avec `Track` et `Metadata` ;
- création d’une playlist à partir d’un dossier ;
- création d’une playlist personnalisée ;
- ajout et retrait de morceaux ;
- sauvegarde et ouverture d’une playlist XSPF ;
- principales options du CLI ;
- lecture audio d’un MP3 ou d’un FLAC depuis les services et le CLI ;
- pause, reprise et arrêt au niveau du service audio ;
- première version de la GUI ;
- ouverture d’un fichier ou d’un dossier depuis la GUI ;
- affichage et modification des métadonnées depuis la GUI ;
- création, modification, sauvegarde et ouverture de playlists depuis la GUI ;
- premiers tests automatiques des services, du CLI, des playlists et de l’audio.

## Fonctionnalités commencées mais incomplètes

Les éléments suivants ont déjà une base, mais doivent encore être finalisés :

- finalisation des messages d’aide et d’erreur du CLI ;
- réouverture et lecture d’une playlist XSPF depuis le CLI ;
- branchement des boutons audio dans la GUI ;
- enchaînement d’une playlist avec la boucle `after()` de Tkinter ;
- amélioration de la navigation et de la lisibilité de la GUI ;
- intégration complète entre les services, le CLI et la GUI ;
- extension de la suite de tests automatiques ;
- documentation du code et mise à jour des documents de suivi.

## Fonctionnalités restantes

Les fonctionnalités principales encore à réaliser après le point d’avancement sont :

- recherche des informations complètes d’un album via une API Web ;
- récupération et affichage des paroles de tous les morceaux ;
- gestion des erreurs réseau et des réponses absentes ;
- extraction d’une pochette déjà présente dans un fichier audio ;
- téléchargement d’une pochette lorsqu’elle est absente ;
- affichage et validation de la pochette dans la GUI ;
- sauvegarde de la pochette dans le dossier de l’album ;
- ajout de morceaux à une playlist par glisser-déposer ;
- lecture complète d’une playlist enregistrée dans le CLI ;
- commandes Lire, Pause, Reprendre et Arrêter dans la GUI ;
- affichage du morceau actuellement lu ;
- tests des services API et des pochettes ;
- tests de bout en bout du CLI et de la GUI ;
- génération et vérification de la documentation Doxygen ;
- finalisation du `README.md` et du fichier `repartition.md` ;
- rédaction du rapport ;
- préparation et enregistrement de la vidéo de démonstration ;
- préparation du diaporama et de la soutenance ;
- vérification de l’archive finale et des règles de nommage.

## Organisation de la suite

Après le point d’avancement, le travail reste réparti selon les domaines principaux :

- **Fatma-Zahra :** services API, gestion des erreurs, pochettes et tests des services ;
- **Enzo :** finalisation du CLI, lecture des playlists XSPF, validation XSPF et logique du glisser-déposer ;
- **Sanaa :** intégration audio dans la GUI, glisser-déposer, affichage des pochettes et amélioration de l’interface ;
- **Travail collectif :** intégration, tests complets, documentation, rapport, vidéo, diaporama et préparation du rendu.

## Conclusion

Le point d’avancement montre que les fondations techniques du projet sont en place. Les principaux formats sont reconnus, les métadonnées et les playlists peuvent être manipulées, et la lecture audio fonctionne au niveau des services et du CLI.

Le projet n’est toutefois pas terminé. Les fonctionnalités liées à l’API, aux paroles, aux pochettes, au glisser-déposer et à l’audio dans la GUI représentent encore une partie importante du travail. La prochaine étape consiste donc à finaliser les interfaces, intégrer les fonctionnalités complémentaires et renforcer les tests afin d’obtenir une application stable pour la démonstration et le rendu final.
