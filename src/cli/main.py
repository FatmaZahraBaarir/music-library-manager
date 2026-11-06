import argparse


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

	return args


def main(arguments=None):
	"""
	@brief Lance le programme en ligne de commande.

	@param arguments Arguments à analyser, ou None pour utiliser ceux du terminal.
	@type arguments list de str ou None
	@return Arguments reconnus pendant ce premier bloc du CLI.
	@rtype argparse.Namespace
	"""
	return parse_arguments(arguments)


if __name__ == "__main__":
	main()
