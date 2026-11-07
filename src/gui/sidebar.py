"""
@brief Composant du menu latéral de l'application.
"""

import tkinter as tk


class Sidebar:
	"""
	@brief Regroupe les boutons du menu latéral.
	"""

	def __init__(self, parent, on_open_folder, on_open_file):
		"""
		@brief Construit les boutons du menu.

		@param parent Cadre contenant le menu.
		@type parent tkinter.Frame
		@param on_open_folder Méthode appelée pour ouvrir un dossier.
		@type on_open_folder callable
		@param on_open_file Méthode appelée pour ouvrir un morceau.
		@type on_open_file callable
		"""

		# Création du titre du menu.
		self.menu_title = tk.Label(
			parent,
			text="Ma bibliothèque",
			bg="#f1f5f9",
			fg="#1e293b",
			font=("Arial", 16)
		)
		self.menu_title.pack(padx=15, pady=20)

		# Création du bouton d'accueil.
		self.home_button = tk.Button(
			parent,
			text="Accueil",
		)
		self.home_button.pack(fill=tk.X, padx=15, pady=5)

		# Création du bouton de recherche, en attente de son branchement.
		self.search_button = tk.Button(
			parent,
			text="Recherche",
		)
		self.search_button.pack(fill=tk.X, padx=15, pady=5)


		# Création du bouton d'ouverture d'un dossier.
		self.open_button = tk.Button(
			parent,
			text="Ouvrir un dossier",
			command=on_open_folder
		)
		self.open_button.pack(pady=10)

		# Création du bouton d'ouverture d'un morceau.
		self.open_file_button = tk.Button(
			parent,
			text="Ouvrir un morceau",
			command=on_open_file
		)
		self.open_file_button.pack(pady=10)

		# Création des boutons de gestion des playlists.
		self.open_playlist_button = tk.Button(
			parent,
			text="Ouvrir une playlist"
		)
		self.open_playlist_button.pack(pady=5)

		self.save_playlist_button = tk.Button(
			parent,
			text="Sauvegarder la playlist"
		)
		self.save_playlist_button.pack(pady=5)

		# Création du bouton de création d'une playlist.
		self.create_playlist_button = tk.Button(
			parent,
			text="Créer une playlist",
		)
		self.create_playlist_button.pack(fill=tk.X, padx=15, pady=5)

		# Création du titre de la liste des playlists.
		self.playlists_label = tk.Label(
			parent,
			text="Mes playlists",
			bg="#f1f5f9",
			fg="#1e293b",
			font=("Arial", 12)
		)
		self.playlists_label.pack(padx=15, pady=20)

		# Message affiché tant qu'aucune playlist n'est disponible.
		self.empty_playlists_label = tk.Label(
			parent,
			text="Aucune playlist ouverte",
			bg="#f1f5f9",
			fg="#475569"
		)
		self.empty_playlists_label.pack(padx=15, pady=5)