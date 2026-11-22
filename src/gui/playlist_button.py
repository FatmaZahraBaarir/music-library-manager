"""
@brief Affiche un bouton pour accéder à une playlist.
"""

import tkinter as tk


class PlaylistButton:
	"""
	@brief Associe le nom d'une playlist à son affichage.
	"""

	def __init__(self, cadrePlaylists, playlist, on_open_playlist):
		"""
		@brief Crée le bouton de la playlist.

		@param cadrePlaylists Cadre contenant les boutons.
		@type cadrePlaylists tkinter.Frame
		@param playlist Playlist associée au bouton.
		@type playlist Playlist
		@param on_open_playlist Méthode qui affiche la playlist.
		"""
		self.playlist = playlist
		self.on_open_playlist = on_open_playlist

		# Cadre permettant de mettre en évidence la playlist affichée.
		self.cadre = tk.Frame(cadrePlaylists, bg="#f1f5f9")
		self.cadre.pack(pady=5)

		# Bouton portant le nom de la playlist.
		self.bouton = tk.Button(self.cadre, text=self.playlist.name, command=self.open_playlist)
		self.bouton.pack(padx=3, pady=3)

	def open_playlist(self):
		"""
		@brief Demande l'affichage de la playlist associée.
		"""
		self.on_open_playlist(self.playlist)