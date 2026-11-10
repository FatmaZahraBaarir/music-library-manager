import argparse
import sys
import time
from pathlib import Path


SRC_DIRECTORY = Path(__file__).resolve().parents[1]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))


def create_parser():
	"""
	@brief Crée le parseur des options du programme en ligne de commande.

	@return Parseur configuré avec les options du sujet.
	@rtype argparse.ArgumentParser
	"""
	parser = argparse.ArgumentParser(
		description="Analyse des fichiers audio et gestion des playlists XSPF.",
		add_help=False,
	)
	parser.add_argument(
		"-h",
		"--help",
		action="help",
		help="affiche cette aide et quitte",
	)

	input_group = parser.add_mutually_exclusive_group()
	input_group.add_argument(
		"-f",
		"--file",
		metavar="FICHIER",
		help="analyse un fichier MP3 ou FLAC",
	)
	input_group.add_argument(
		"-d",
		"--directory",
		metavar="DOSSIER",
		help="explore un dossier et ses sous-dossiers",
	)

	parser.add_argument(
		"-o",
		"--output",
		metavar="FICHIER.xspf",
		help="choisit le fichier XSPF produit avec -d",
	)
	parser.add_argument(
		"-p",
		"--play",
		metavar="FICHIER",
		help="lit un fichier audio",
	)
	parser.add_argument("--title", metavar="TITRE", help="modifie le titre avec -f")
	parser.add_argument("--artist", metavar="ARTISTE", help="modifie l'artiste avec -f")
	parser.add_argument("--album", metavar="ALBUM", help="modifie l'album avec -f")
	parser.add_argument("--track-number",metavar="NUMÉRO",help="modifie le numéro de piste avec -f",)
	parser.add_argument("--year", metavar="ANNÉE", help="modifie l'année avec -f")
	return parser


def parse_arguments(arguments=None):
	"""
	@brief Lit les arguments et refuse les combinaisons incorrectes.

	@param arguments Arguments à analyser, ou None pour utiliser ceux du terminal.
	@type arguments list de str ou None
	@return Arguments reconnus par le parseur.
	@rtype argparse.Namespace
	@raise SystemExit Si les arguments sont absents ou incompatibles.
	"""
	parser = create_parser()
	args = parser.parse_args(arguments)

	if not args.file and not args.directory and not args.play:
		parser.error("aucun argument fourni ; utilisez -h pour afficher l'aide")

	if args.output and not args.directory:
		parser.error("-o/--output doit être utilisé avec -d/--directory")

	metadata_values = (
		args.title,
		args.artist,
		args.album,
		args.track_number,
		args.year,
	)
	if any(value is not None for value in metadata_values) and not args.file:
		parser.error("les options de métadonnées doivent être utilisées avec -f/--file")

	return args


def process_directory(args, library_service):
	"""
	@brief Explore un dossier et sauvegarde la playlist XSPF obtenue.

	@param args Arguments contenant le dossier et le chemin de sortie éventuel.
	@type args argparse.Namespace
	@param library_service Service principal de la bibliothèque musicale.
	@type library_service LibraryInterface
	@return Code de succès du traitement.
	@rtype int
	"""
	output_path = Path(args.output or "default_playlist.xspf")
	playlist = library_service.create_playlist_from_directory(
		args.directory,
		output_path,
	)

	print(f"Playlist créée : {playlist.file_path}")
	print(f"{len(playlist.tracks)} morceau(x) trouvé(s) :")
	for track in playlist.tracks:
		print(f"- {track.file_path}")

	return 0


def process_file(args, library_service):
	"""
	@brief Lit et affiche les métadonnées du fichier audio demandé.

	@param args Arguments contenant le chemin du fichier audio.
	@type args argparse.Namespace
	@param library_service Service principal de la bibliothèque musicale.
	@type library_service LibraryInterface
	@return Code de succès du traitement.
	@rtype int
	"""
	metadata_values = (
		args.title,
		args.artist,
		args.album,
		args.track_number,
		args.year,
	)

	metadata_update_requested = False
	# Examine les valeurs une par une jusqu'à en trouver une renseignée
	for value in metadata_values:
		if value is not None:
			metadata_update_requested = True
			break

	if metadata_update_requested:
		metadata = library_service.update_metadata_from_text(
			file_path=args.file,
			title_text=args.title,
			artist_text=args.artist,
			album_title_text=args.album,
			track_number_text=args.track_number,
			year_text=args.year,
		)
		print("Métadonnées modifiées et relues avec succès.")
	else:
		# Utilise le service commun au CLI et à la GUI pour lire le fichier
		metadata = library_service.read_metadata(args.file)

	# Remplace les informations absentes par un message lisible
	title = metadata.title or "Non renseigné"
	artist = metadata.artist or "Non renseigné"
	album_title = metadata.album_title or "Non renseigné"
	track_number = metadata.track_number or "Non renseigné"
	year = metadata.year or "Non renseigné"

	print(f"Fichier : {args.file}")
	print(f"Titre : {title}")
	print(f"Artiste : {artist}")
	print(f"Album : {album_title}")
	print(f"Piste : {track_number}")
	print(f"Année : {year}")

	return 0


def process_play(args, library_service):
	"""Démarre un fichier audio et garde le CLI actif jusqu'à sa fin."""
	file_path = args.play

	try:
		library_service.play_track(file_path)
		print(f"Lecture en cours : {file_path}")

		# Vérifie si le morceau est encore en cours
		playback_in_progress = library_service.is_playing()
		while playback_in_progress:
			time.sleep(0.1)
			playback_in_progress = library_service.is_playing()

	except KeyboardInterrupt:
		library_service.stop_playback()
		print("Lecture arrêtée.")
		return 0

	print("Lecture terminée.")
	return 0


def main(arguments=None, library_service=None):
	"""
	@brief Lance le programme en ligne de commande.

	@param arguments Arguments à analyser, ou None pour utiliser ceux du terminal.
	@type arguments list de str ou None
	@param library_service Service fourni, ou None pour utiliser le service réel.
	@type library_service LibraryInterface ou None
	@return Code de sortie du programme.
	@rtype int
	"""
	args = parse_arguments(arguments)

	if args.file or args.directory or args.play:
		try:
			if library_service is None:
				from library.services.library_service import LibraryService
				library_service = LibraryService()
			if args.directory:
				return process_directory(args, library_service)

			if args.file:
				return process_file(args, library_service)

			if args.play:
				return process_play(args, library_service)
		except ImportError as error:
			print(f"Erreur : dépendance Python absente ({error}).", file=sys.stderr)
			return 1
		except (OSError, ValueError) as error:
			print(f"Erreur : {error}", file=sys.stderr)
			return 1

	return 0


if __name__ == "__main__":
	raise SystemExit(main())
