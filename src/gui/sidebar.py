"""
@brief Affiche le menu à gauche de la fenêtre.
"""

import tkinter as tk

class Sidebar:
	"""
	@brief Regroupe les boutons et la zone des playlists.
	"""

	def __init__(self, cadreMenu, on_create_playlist, on_home):
		"""
		@brief Crée les éléments du menu.

		@param cadreMenu Cadre du menu à gauche.
		@type cadreMenu tkinter.Frame
		@param on_create_playlist Méthode qui affiche le formulaire de création d'une playlist.
		@param on_home Méthode qui affiche la page de bienvenue.
		"""
		# Titre du menu.
		self.menu_title = tk.Label(cadreMenu, text="Ma bibliothèque", bg="#f1f5f9", fg="#1e293b", font=("Arial", 16))
		self.menu_title.pack(padx=15, pady=20)

		# Cadre permettant de mettre en évidence la page d'accueil.
		self.cadreAccueil = tk.Frame(cadreMenu, bg="#f1f5f9")
		self.cadreAccueil.pack(padx=15, pady=5)

		self.home_button = tk.Button(self.cadreAccueil, text="Accueil", command=on_home)
		self.home_button.pack(padx=3, pady=3)

		# Bouton de recherche, pas encore relié à une action.
		self.search_button = tk.Button(cadreMenu, text="Recherche - À venir")
		self.search_button.pack(padx=15, pady=5)

		# Cadre permettant de mettre en évidence le formulaire de création.
		self.cadreCreation = tk.Frame(cadreMenu, bg="#f1f5f9")
		self.cadreCreation.pack(padx=15, pady=5)

		self.create_playlist_button = tk.Button(self.cadreCreation, text="Créer une playlist",command=on_create_playlist)
		self.create_playlist_button.pack(padx=3, pady=3)

		# Zone réservée aux playlists.
		self.playlists_label = tk.Label(cadreMenu, text="Mes playlists", bg="#f1f5f9", fg="#1e293b", font=("Arial", 12))
		self.playlists_label.pack(padx=15, pady=20)

		# Cadre contenant les boutons des playlists.
		self.cadrePlaylists = tk.Frame(cadreMenu, bg="#f1f5f9")
		self.cadrePlaylists.pack(padx=15, pady=5)

		# Message affiché tant qu'aucune playlist n'est ouverte ou créée.
		self.empty_playlists_label = tk.Label(cadreMenu, text="Aucune playlist", bg="#f1f5f9", fg="#475569")
		self.empty_playlists_label.pack(padx=15, pady=5)