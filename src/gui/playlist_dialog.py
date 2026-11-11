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
		@param on_playlist_created Méthode appelée après validation du nom pour transmettre la playlist créée.
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

		# Cadre contenant le menu d’ajout des morceaux.
		self.cadreChoix = tk.Frame(cadrePlaylist, bg="#ffffff")
		self.cadreChoix.pack(pady=10)

		# Menu d'ajout : morceaux sélectionnés ou dossier entier.
		self.ajouter_button = tk.Menubutton(self.cadreChoix, text="Ajouter", relief=tk.RAISED)
		self.ajouter_button.pack(padx=5)

		self.menuAjout = tk.Menu(self.ajouter_button, tearoff=False)
		self.menuAjout.add_command(label="Des morceaux", command=self.choose_track)
		self.menuAjout.add_command(label="Un dossier", command=self.choose_folder)
		self.ajouter_button.config(menu=self.menuAjout)

		# Affichage des morceaux choisis.
		self.morceaux_list = tk.Listbox(cadrePlaylist, width=45, height=10, bg="#f1f5f9", fg="#1e293b")
		self.morceaux_list.pack(padx=10, pady=10)

		# Cadre regroupant les boutons de validation.
		self.cadreValidation = tk.Frame(cadrePlaylist, bg="#ffffff")
		self.cadreValidation.pack(pady=10)

		# Validation ou annulation.
		self.creer_button = tk.Button(self.cadreValidation, text="Créer", command=self.create_playlist)
		self.creer_button.pack(side=tk.LEFT, padx=5)

		self.annuler_button = tk.Button(self.cadreValidation, text="Annuler", command=on_cancel)
		self.annuler_button.pack(side=tk.LEFT, padx=5)

	def choose_track(self):
		"""
		@brief Ajoute les fichiers audio sélectionnés à la playlist.
		"""
		cheminsFichiers = filedialog.askopenfilenames(title="Choisir des morceaux", filetypes=[("Fichiers audio", "*.mp3 *.flac")])

		if len(cheminsFichiers) == 0:
			return

		nombreAjoutes = 0
		nombreErreurs = 0

		# Ajout de chaque fichier ; un fichier invalide n'empêche pas les suivants.
		for cheminFichier in cheminsFichiers:
			try:
				morceau = self.library_service.add_track_to_playlist(self.playlist, cheminFichier)
			except ValueError:
				nombreErreurs += 1
			else:
				# Affichage du nom du fichier uniquement.
				cheminTexte = str(morceau.file_path)
				position = len(cheminTexte) - 1
				while position > 0 and cheminTexte[position] != "/":
					position -= 1

				nomFichier = cheminTexte[position + 1:]
				self.morceaux_list.insert(tk.END, nomFichier)
				nombreAjoutes += 1

		message = str(nombreAjoutes) + " morceau(x) ajouté(s)."
		if nombreErreurs > 0:
			message += "\n" + str(nombreErreurs) + " fichier(s) n'ont pas pu être lus."

		messagebox.showinfo("Ajout des morceaux", message)

	def choose_folder(self):
		"""
		@brief Ajoute les morceaux d'un dossier et de ses sous-dossiers.
		"""
		cheminDossier = filedialog.askdirectory(title="Choisir un dossier de musique")

		if cheminDossier == "":
			return

		# Recherche des fichiers MP3 et FLAC par le service existant.
		try:
			fichiersAudio = self.library_service.find_audio_files(cheminDossier)
		except ValueError as erreur:
			messagebox.showwarning("Dossier inaccessible", str(erreur))
			return

		if len(fichiersAudio) == 0:
			messagebox.showinfo("Aucun morceau", "Aucun fichier MP3 ou FLAC reconnu dans ce dossier.")
			return

		nombreAjoutes = 0
		nombreErreurs = 0

		# Position du début du chemin relatif, commune à tous les morceaux.
		debutChemin = len(cheminDossier)
		if cheminDossier[-1] != "/":
			debutChemin += 1

		# Ajout des morceaux en conservant ceux déjà sélectionnés.
		for cheminFichier in fichiersAudio:
			try:
				morceau = self.library_service.add_track_to_playlist(self.playlist, cheminFichier)
			except ValueError:
				nombreErreurs += 1
			else:
				# Affichage du chemin relatif au dossier choisi.
				cheminRelatif = str(morceau.file_path)[debutChemin:]
				self.morceaux_list.insert(tk.END, cheminRelatif)
				nombreAjoutes += 1

		message = str(nombreAjoutes) + " morceau(x) ajouté(s)."

		if nombreErreurs > 0:
			message += "\n" + str(nombreErreurs) + " fichier(s) n'ont pas pu être lus."

		messagebox.showinfo("Ajout du dossier", message)

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