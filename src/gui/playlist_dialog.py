"""
@brief Affiche le formulaire de création d'une playlist.
"""

import tkinter as tk
from tkinter import filedialog, messagebox


class PlaylistDialog:
	"""
	@brief Permet de nommer une playlist et de choisir ses morceaux.
	"""

	def __init__(self, cadrePlaylist, library_service, on_playlist_created, on_cancel):
		"""
		@brief Crée les champs et les boutons du formulaire.

		@param cadrePlaylist Cadre contenant le formulaire.
		@type cadrePlaylist tkinter.Frame
		@param library_service Service de la bibliothèque.
		@type library_service LibraryService
		@param on_playlist_created Méthode appelée pour valider la playlist.
		@param on_cancel Méthode appelée pour annuler.
		"""
		self.library_service = library_service
		self.on_playlist_created = on_playlist_created

		# Playlist préparée avant la validation.
		self.playlist = self.library_service.create_empty_playlist("")

		# Titre du formulaire.
		self.titre_label = tk.Label(cadrePlaylist, text="Créer une playlist", font=("Arial", 16), bg="#ffffff", fg="#1e293b")
		self.titre_label.pack(pady=15)

		# Saisie du nom de la playlist.
		self.nom_label = tk.Label(cadrePlaylist, text="Nom de la playlist", bg="#ffffff", fg="#1e293b")
		self.nom_label.pack(pady=5)

		self.nom_var = tk.StringVar()
		self.nom_entry = tk.Entry(cadrePlaylist, textvariable=self.nom_var, width=35, bg="#f1f5f9", fg="#1e293b")
		self.nom_entry.pack(pady=5)

		# Choix des fichiers audio, un par un.
		self.choisir_button = tk.Button(cadrePlaylist, text="Choisir un morceau", command=self.choose_track)
		self.choisir_button.pack(pady=10)

		# Affichage des morceaux choisis.
		self.morceaux_list = tk.Listbox(cadrePlaylist, width=45, height=10, bg="#f1f5f9", fg="#1e293b")
		self.morceaux_list.pack(padx=10, pady=10)

		# Validation ou annulation.
		self.creer_button = tk.Button(cadrePlaylist, text="Créer", command=self.create_playlist)
		self.creer_button.pack(pady=5)

		self.annuler_button = tk.Button(cadrePlaylist, text="Annuler", command=on_cancel)
		self.annuler_button.pack(pady=5)

	def choose_track(self):
		"""
		@brief Ajoute le fichier choisi à la playlist.
		"""
		cheminFichier = filedialog.askopenfilename(title="Choisir un morceau", filetypes=[("Fichiers MP3", "*.mp3"), ("Fichiers FLAC", "*.flac")])

		if cheminFichier == "":
			return

		# Vérification et ajout du morceau par le service.
		try:
			morceau = self.library_service.add_track_to_playlist(self.playlist, cheminFichier)
		except ValueError as erreur:
			messagebox.showwarning("Ajout impossible", str(erreur))
			return

		self.morceaux_list.insert(tk.END, str(morceau.file_path))

	def create_playlist(self):
		"""
		@brief Vérifie le nom et valide la playlist.
		"""
		nomPlaylist = self.nom_var.get().strip()

		if nomPlaylist == "":
			messagebox.showwarning("Nom manquant", "Saisissez un nom pour la playlist.")
			return

		self.playlist.name = nomPlaylist
		self.on_playlist_created(self.playlist)