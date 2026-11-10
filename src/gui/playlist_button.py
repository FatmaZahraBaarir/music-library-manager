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

		# Bouton portant le nom de la playlist.
		self.bouton = tk.Button(cadrePlaylists, text=self.playlist.name, command=self.open_playlist)
		self.bouton.pack(pady=5)

	def open_playlist(self):
		"""
		@brief Demande l'affichage de la playlist associée.
		"""
		self.on_open_playlist(self.playlist)