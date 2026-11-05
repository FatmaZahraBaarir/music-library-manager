import tkinter as tk


class MainWindow:
	"""
	@brief Représente la fenêtre principale de l'application.

	@param root Fenêtre principale Tkinter.
	@type root tkinter.Tk
	"""

	def __init__(self, root):
		"""
		@brief Initialise la fenêtre principale.

		@param root Fenêtre principale Tkinter.
		@type root tkinter.Tk
		"""
		self.root = root
		self.root.title("Gestionnaire de bibliothèque musicale")
		self.root.geometry("800x800")

		# Création du titre de la fenêtre.
		self.title_label = tk.Label(self.root, text="Bibliothèque musicale", font=("Arial", 18))
		self.title_label.pack(pady=20)

		# Création du bouton d'ouverture d'un dossier.
		self.open_button = tk.Button(self.root, text="Ouvrir un dossier")
		self.open_button.pack(pady=10)

		# Création du titre de la liste des fichiers.
		self.files_label = tk.Label(self.root, text="Fichiers audio")
		self.files_label.pack(pady=10)

		# Création de la liste des fichiers audio.
		self.files_list = tk.Listbox(self.root, width=50, height=8)
		self.files_list.pack(pady=10)

		# Création de la zone des métadonnées.
		self.metadata_label = tk.Label(self.root, text="Métadonnées du morceau")
		self.metadata_label.pack(pady=10)

		self.metadata_text = tk.Label(self.root, text="Aucun morceau sélectionné")
		self.metadata_text.pack(pady=5)

		# Création de la zone de la pochette.
		self.cover_label = tk.Label(self.root, text="Pochette de l'album", relief=tk.SOLID, width=25, height=6)
		self.cover_label.pack(pady=10)

		# Création de la zone de playlist.
		self.playlist_label = tk.Label(self.root, text="Playlist")
		self.playlist_label.pack(pady=10)

		self.playlist_list = tk.Listbox(self.root, width=50, height=5)
		self.playlist_list.pack(pady=10)

		# Création des boutons de gestion de la playlist.
		self.open_playlist_button = tk.Button(self.root, text="Ouvrir une playlist")
		self.open_playlist_button.pack(pady=5)

		self.save_playlist_button = tk.Button(self.root, text="Sauvegarder la playlist")
		self.save_playlist_button.pack(pady=5)

		# Création des boutons de lecture.
		self.play_button = tk.Button(self.root, text="Lire")
		self.play_button.pack(pady=5)

		self.stop_button = tk.Button(self.root, text="Arrêter")
		self.stop_button.pack(pady=5)