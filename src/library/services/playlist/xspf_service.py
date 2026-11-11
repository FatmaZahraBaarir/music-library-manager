from pathlib import Path
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlparse

from library.models.playlist import Playlist
from library.models.track import AudioFormat, Track


XSPF_NAMESPACE = "http://xspf.org/ns/0/"
XSPF_TAG = f"{{{XSPF_NAMESPACE}}}"


class XspfService:
	"""Crée, sauvegarde et ouvre des playlists XSPF."""

	def save_playlist(self, playlist, output_path):
		"""
		@brief Sauvegarde une playlist dans un fichier XSPF.

		@param playlist Playlist à sauvegarder.
		@type playlist Playlist
		@param output_path Chemin du fichier à créer.
		@type output_path str ou pathlib.Path
		"""
		#Chemin de sortie
		output_path = Path(output_path)

		# Crée la balise principale de la playlist
		ET.register_namespace("", XSPF_NAMESPACE)
		root = ET.Element(XSPF_TAG + "playlist", {"version": "1"})

		# Ajoute le nom et la liste des morceaux
		ET.SubElement(root, XSPF_TAG + "title").text = playlist.name
		track_list = ET.SubElement(root, XSPF_TAG + "trackList")

		# Ajoute chaque morceau dans la liste
		for track in playlist.tracks:
			track_element = ET.SubElement(track_list, XSPF_TAG + "track")
			location = ET.SubElement(track_element, XSPF_TAG + "location")
			location.text = Path(track.file_path).resolve().as_uri()

		# Indente le XML avec des tabulations pour le rendre lisible
		tree = ET.ElementTree(root)
		ET.indent(tree, space="	", level=0)
		tree.write(output_path, encoding="utf-8", xml_declaration=True)
		playlist.file_path = output_path

	def load_playlist(self, file_path):
		"""
		@brief Ouvre une playlist XSPF.
		@param file_path Chemin du fichier à ouvrir.
		@type file_path str ou pathlib.Path
		@return Playlist trouvée dans le fichier.
		@rtype Playlist
		"""
		file_path = Path(file_path)
		if not file_path.is_file():
			raise ValueError("Le fichier XSPF n'existe pas.")
		if file_path.suffix.lower() != ".xspf":
			raise ValueError("Le fichier doit être au format XSPF.")

		# Lit le fichier et récupère son titre
		try:
			root = ET.parse(file_path).getroot()
		except ET.ParseError as error:
			raise ValueError("Le fichier XSPF contient un XML invalide.") from error

		# Vérifie le contenu de la playlist
		if root.tag != XSPF_TAG + "playlist" or root.attrib.get("version") != "1":
			raise ValueError("Le fichier ne contient pas une playlist XSPF valide.")

		title = root.findtext(XSPF_TAG + "title")
		track_list = root.find(XSPF_TAG + "trackList")
		if title is None or track_list is None:
			raise ValueError("Le fichier ne contient pas une playlist XSPF valide.")

		# Récupère les morceaux de la playlist
		tracks = []
		location_tag = XSPF_TAG + "trackList/" + XSPF_TAG + "track/" + XSPF_TAG + "location"
		for location in root.findall(location_tag):
			if location.text is None:
				raise ValueError("Chemin du morceau manquant.")
			track_path = Path(unquote(urlparse(location.text).path))

			if track_path.suffix.lower() == ".mp3":
				audio_format = AudioFormat.MP3
			elif track_path.suffix.lower() == ".flac":
				audio_format = AudioFormat.FLAC
			else:
				raise ValueError("Format audio non pris en charge.")

			tracks.append(Track(track_path, audio_format))

		# Crée la playlist trouvée dans le fichier
		return Playlist(title, file_path=file_path, tracks=tracks)
