"""
@brief Affiche le menu à gauche de la fenêtre.
"""

import tkinter as tk

class Sidebar:
	"""
	@brief Regroupe les boutons et la liste des playlists du menu.
	"""

	def __init__(self, cadreMenu, on_open_folder, on_open_file):
		"""
		@brief Crée les éléments du menu.

		@param cadreMenu Cadre du menu à gauche.
		@type cadreMenu tkinter.Frame
		@param on_open_folder Méthode qui ouvre un dossier.
		@param on_open_file Méthode qui ouvre un fichier audio.
		"""
		# Titre du menu.
		self.menu_title = tk.Label(cadreMenu, text="Ma bibliothèque", bg="#f1f5f9", fg="#1e293b", font=("Arial", 16))
		self.menu_title.pack(padx=15, pady=20)

		# Bouton d'accueil, pas encore relié à une action.
		self.home_button = tk.Button(cadreMenu, text="Accueil")
		self.home_button.pack(padx=15, pady=5)

		# Bouton de recherche, pas encore relié à une action.
		self.search_button = tk.Button(cadreMenu, text="Recherche")
		self.search_button.pack(padx=15, pady=5)

		# Ouverture d'un dossier de musique.
		self.open_button = tk.Button(cadreMenu, text="Ouvrir un dossier", command=on_open_folder)
		self.open_button.pack(padx=15, pady=10)

		# Ouverture d'un fichier audio.
		self.open_file_button = tk.Button(cadreMenu, text="Ouvrir un morceau", command=on_open_file)
		self.open_file_button.pack(padx=15, pady=10)

		# Boutons de playlist, pas encore reliés aux services.
		self.open_playlist_button = tk.Button(cadreMenu, text="Ouvrir une playlist")
		self.open_playlist_button.pack(padx=15, pady=5)

		self.save_playlist_button = tk.Button(cadreMenu, text="Sauvegarder la playlist")
		self.save_playlist_button.pack(padx=15, pady=5)

		self.create_playlist_button = tk.Button(cadreMenu, text="Créer une playlist")
		self.create_playlist_button.pack(padx=15, pady=5)

		# Zone réservée aux playlists.
		self.playlists_label = tk.Label(cadreMenu, text="Mes playlists", bg="#f1f5f9", fg="#1e293b", font=("Arial", 12))
		self.playlists_label.pack(padx=15, pady=20)

		self.empty_playlists_label = tk.Label(cadreMenu, text="Aucune playlist ouverte", bg="#f1f5f9", fg="#475569")
		self.empty_playlists_label.pack(padx=15, pady=5)