"""
@brief Gère la fenêtre principale du gestionnaire musical.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

from gui.sidebar import Sidebar
from gui.player_bar import PlayerBar
from gui.library_view import LibraryView
from gui.metadata_dialog import MetadataForm
from gui.playlist_dialog import PlaylistDialog
from gui.playlist_button import PlaylistButton

class MainWindow:
	"""
	@brief Réunit les différentes parties de l'interface.
	"""

	def __init__(self, fenetre, library_service):
		"""
		@brief Crée les cadres et les éléments de la fenêtre.

		@param fenetre Fenêtre de l'application.
		@type fenetre tkinter.Tk
		@param library_service Service utilisé pour les fichiers et les métadonnées.
		@type library_service LibraryService
		"""
		self.fenetre = fenetre
		self.library_service = library_service

		# Liste des fichiers ouverts et morceau sélectionné.
		self.audio_files = []

		# Fichiers à retrouver lors du retour à l'accueil.
		self.fichiersBibliotheque = []

		self.selected_track = None

		# Playlist en cours de création ou de modification.
		self.playlist = None

		# Playlists créées ou ouvertes pendant l'utilisation de l'application.
		self.playlists = []

		self.fenetre.title("Gestionnaire de bibliothèque musicale")
		self.fenetre.geometry("1200x750")

		# Barre de lecture en bas.
		self.cadreLecteur = tk.Frame(self.fenetre, bg="#f1f5f9", height=90)
		self.cadreLecteur.pack(side=tk.BOTTOM, fill=tk.X)
		self.player_bar = PlayerBar(self.cadreLecteur)

		# Menu à gauche.
		self.cadreMenu = tk.Frame(self.fenetre, bg="#f1f5f9", width=200)
		self.cadreMenu.pack(side=tk.LEFT, fill=tk.Y)
		self.sidebar = Sidebar(self.cadreMenu, self.on_open_folder, self.on_open_file, self.on_create_playlist,
		                       self.on_load_playlist, self.on_home)

		# Cadre contenant la bibliothèque et les métadonnées.
		self.cadrePrincipal = tk.Frame(self.fenetre, bg="#ffffff")
		self.cadrePrincipal.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		# Bibliothèque au centre.
		self.cadreBibliotheque = tk.Frame(self.cadrePrincipal, bg="#ffffff")
		self.cadreBibliotheque.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)
		self.library_view = LibraryView(self.cadreBibliotheque, self.on_file_selected)

		# Informations du morceau à droite.
		self.cadreMetadonnees = tk.Frame(self.cadrePrincipal, bg="#ffffff")
		self.cadreMetadonnees.pack(side=tk.RIGHT, fill=tk.Y, padx=15, pady=10)

		# Emplacement carré de la pochette.
		self.cover_canvas = tk.Canvas(self.cadreMetadonnees, width=160, height=160, bg="#f1f5f9")
		self.cover_canvas.pack(pady=10)
		self.cover_canvas.create_text(80, 80, text="Pochette indisponible", fill="#475569", font=("Arial", 10))

		# Titre du panneau de droite.
		self.metadata_label = tk.Label(self.cadreMetadonnees, text="Métadonnées du morceau", bg="#ffffff", fg="#1e293b")
		self.metadata_label.pack(pady=10)

		# Informations du morceau ou message destiné à l'utilisateur.
		self.metadata_message = tk.StringVar()
		self.metadata_message.set("Aucun morceau sélectionné")

		self.metadata_text = tk.Label(self.cadreMetadonnees, textvariable=self.metadata_message, bg="#ffffff", fg="#1e293b")
		self.metadata_text.pack(pady=5)

		# Formulaire de modification.
		self.metadata_form = MetadataForm(self.cadreMetadonnees, self.on_save_metadata)

	def on_open_file(self):
		"""
		@brief Affiche le fichier choisi dans la bibliothèque.
		"""
		# Choix d'un fichier audio.
		cheminFichier = filedialog.askopenfilename(parent=self.fenetre, title="Choisir un morceau", filetypes=[("Fichiers MP3", "*.mp3"), ("Fichiers FLAC", "*.flac")])

		# Arrêt si l'utilisateur annule.
		if cheminFichier == "":
			return

		# Retour à la bibliothèque.
		self.show_library()

		# Affichage du fichier choisi.
		self.audio_files = [cheminFichier]
		self.fichiersBibliotheque = self.audio_files.copy()
		self.library_view.files_list.delete(0, tk.END)
		self.library_view.files_list.insert(tk.END, cheminFichier)

		# Effacement des informations du morceau précédent.
		self.selected_track = None
		self.metadata_message.set("Aucun morceau sélectionné")
		self.metadata_form.clear_fields()

	def on_open_folder(self):
		"""
		@brief Affiche les fichiers audio du dossier choisi.
		"""
		# Choix d'un dossier.
		cheminDossier = filedialog.askdirectory(parent=self.fenetre, title="Choisir un dossier de musique")

		if cheminDossier == "":
			return

		# Recherche des fichiers par le service.
		try:
			fichiersAudio = self.library_service.find_audio_files(cheminDossier)
		except ValueError as erreur:
			self.metadata_message.set(str(erreur))
			return

		# Retour à la bibliothèque.
		self.show_library()

		self.audio_files = fichiersAudio
		self.fichiersBibliotheque = self.audio_files.copy()

		# Effacement de la liste et des informations précédentes.
		self.library_view.files_list.delete(0, tk.END)
		self.selected_track = None
		self.metadata_message.set("Aucun morceau sélectionné")
		self.metadata_form.clear_fields()

		# Message si aucun fichier audio n'est trouvé.
		if len(self.audio_files) == 0:
			self.metadata_message.set("Aucun fichier MP3 ou FLAC reconnu dans ce dossier.")
			return

		# Affichage des chemins des fichiers.
		for cheminFichier in self.audio_files:
			self.library_view.files_list.insert(tk.END, str(cheminFichier))

	def on_file_selected(self):
		"""
		@brief Remplit le formulaire avec les informations du morceau choisi.
		"""
		# Position du morceau sélectionné dans la liste.
		selection = self.library_view.files_list.curselection()

		if len(selection) == 0:
			return

		cheminFichier = self.audio_files[selection[0]]

		# Lecture du morceau par le service.
		try:
			self.selected_track = self.library_service.read_track(cheminFichier)
		except ValueError as erreur:
			self.selected_track = None
			self.metadata_form.clear_fields()
			self.metadata_message.set(str(erreur))
			return

		# Affichage des métadonnées dans les champs.
		metadata = self.selected_track.metadata
		self.metadata_form.display_metadata(metadata)

		# Conversion de la durée en minutes et secondes.
		duree = self.selected_track.duration_seconds

		if duree is None:
			texteDuree = "Non renseignée"
		else:
			totalSecondes = int(duree)
			minutes = totalSecondes // 60
			secondes = totalSecondes % 60

			# Ajout du zéro pour afficher, par exemple, 0:03.
			if secondes < 10:
				texteDuree = str(minutes) + ":0" + str(secondes)
			else:
				texteDuree = str(minutes) + ":" + str(secondes)

		# Le format et la durée ne sont pas modifiables.
		texte = f"Format : {self.selected_track.format.value.upper()}\nDurée : {texteDuree}"
		self.metadata_message.set(texte)

	def on_save_metadata(self):
		"""
		@brief Enregistre les modifications après confirmation.
		"""
		# Un morceau doit être choisi avant l'enregistrement.
		if self.selected_track is None:
			self.metadata_message.set("Sélectionnez un morceau avant d'enregistrer.")
			return

		# Confirmation de l'utilisateur.
		confirmation = messagebox.askyesno("Enregistrer les métadonnées", "Voulez-vous enregistrer les modifications dans ce fichier audio ?", parent=self.fenetre)

		if confirmation == False:
			return

		# Envoi des valeurs saisies au service.
		try:
			metadata = self.library_service.update_metadata_from_text(file_path=self.selected_track.file_path, title_text=self.metadata_form.title_var.get(), artist_text=self.metadata_form.artist_var.get(), album_title_text=self.metadata_form.album_var.get(), track_number_text=self.metadata_form.track_number_var.get(), year_text=self.metadata_form.year_var.get())
		except ValueError as erreur:
			self.metadata_message.set(str(erreur))
			return

		# Mise à jour des métadonnées gardées en mémoire.
		self.selected_track.metadata = metadata
		self.metadata_message.set("Métadonnées enregistrées.")

	def on_create_playlist(self):
		"""
		@brief Affiche le formulaire de création au centre.
		"""
		# Remplacement de la bibliothèque par le formulaire.
		self.cadreBibliotheque.destroy()
		self.cadreBibliotheque = tk.Frame(self.cadrePrincipal, bg="#ffffff")
		self.cadreBibliotheque.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)

		self.playlist_form = PlaylistDialog(self.cadreBibliotheque, self.library_service, self.on_playlist_created,
		                                    self.on_home)

	def show_library(self):
		"""
		@brief Affiche la bibliothèque à la place du formulaire.
		"""
		# Reconstruction de la liste centrale.
		self.cadreBibliotheque.destroy()
		self.cadreBibliotheque = tk.Frame(self.cadrePrincipal, bg="#ffffff")
		self.cadreBibliotheque.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)

		self.library_view = LibraryView(self.cadreBibliotheque, self.on_file_selected)

		# Affichage des fichiers déjà ouverts.
		for cheminFichier in self.audio_files:
			self.library_view.files_list.insert(tk.END, str(cheminFichier))

	def on_playlist_created(self, playlist):
		"""
		@brief Conserve la playlist et ajoute son bouton au menu.

		@param playlist Nouvelle playlist.
		@type playlist Playlist
		"""
		self.playlists.append(playlist)
		self.playlist = playlist

		# Effacement du message affiché avant la première création.
		self.sidebar.empty_playlists_label.config(text="")

		# Ajout du bouton permettant d'ouvrir cette playlist.
		PlaylistButton(self.sidebar.cadrePlaylists, playlist, self.on_open_playlist)

		# Affichage des morceaux après la création.
		self.on_open_playlist(playlist)

	def on_open_playlist(self, playlist):
		"""
		@brief Affiche les morceaux de la playlist au centre.

		@param playlist Playlist à afficher.
		@type playlist Playlist
		"""
		self.playlist = playlist

		# Récupération des fichiers de la playlist.
		self.audio_files = []
		for morceau in playlist.tracks:
			self.audio_files.append(morceau.file_path)

		# Effacement des informations du morceau précédent.
		self.selected_track = None
		self.metadata_form.clear_fields()
		self.metadata_message.set("Aucun morceau sélectionné")

		# Affichage des morceaux au centre.
		self.show_library()
		self.library_view.files_label.config(text=playlist.name)
		self.library_view.instructions_label.config(text="Sélectionnez un morceau, puis cliquez sur « Afficher les métadonnées ».")

		# Ajout d'un morceau à la playlist.
		self.ajouter_morceau_button = tk.Button(self.library_view.cadreBoutons, text="Ajouter un morceau",
		                                        command=self.on_add_track)
		self.ajouter_morceau_button.pack(side=tk.LEFT, padx=5)

		# Retrait du morceau sélectionné dans la playlist.
		self.retirer_morceau_button = tk.Button(self.library_view.cadreBoutons, text="Retirer le morceau", command=self.on_remove_track)
		self.retirer_morceau_button.pack(side=tk.LEFT, padx=5)

		# Enregistrement de la playlist.
		self.enregistrer_playlist_button = tk.Button(self.library_view.cadreBoutons, text="Enregistrer la playlist",
		                                             command=self.on_save_playlist)
		self.enregistrer_playlist_button.pack(side=tk.LEFT, padx=5)

	def on_save_playlist(self):
		"""
		@brief Enregistre la playlist dans un fichier XSPF.
		"""
		if self.playlist is None:
			messagebox.showwarning("Aucune playlist", "Créez ou ouvrez une playlist avant d'enregistrer.", parent=self.fenetre)
			return

		# Choix de l'emplacement du fichier.
		cheminPlaylist = filedialog.asksaveasfilename(parent=self.fenetre, title="Enregistrer la playlist", defaultextension=".xspf", filetypes=[("Playlist XSPF", "*.xspf")])

		if cheminPlaylist == "":
			return

		# Enregistrement par le service.
		try:
			self.library_service.save_playlist(self.playlist, cheminPlaylist)
		except (ValueError, OSError) as erreur:
			messagebox.showwarning("Enregistrement impossible", str(erreur), parent=self.fenetre)
			return

		messagebox.showinfo("Playlist enregistrée", "La playlist a été enregistrée.", parent=self.fenetre)


	def on_load_playlist(self):
		"""
		@brief Ouvre une playlist enregistrée dans un fichier XSPF.
		"""
		# Choix du fichier playlist.
		cheminPlaylist = filedialog.askopenfilename(parent=self.fenetre, title="Ouvrir une playlist", filetypes=[("Playlist XSPF", "*.xspf")])

		if cheminPlaylist == "":
			return

		# Affichage de la playlist si ce fichier est déjà ouvert.
		for playlistOuverte in self.playlists:
			if str(playlistOuverte.file_path) == cheminPlaylist:
				self.on_open_playlist(playlistOuverte)
				return

		# Lecture de la playlist par le service.
		try:
			playlist = self.library_service.load_playlist(cheminPlaylist)
		except (ValueError, OSError) as erreur:
			messagebox.showwarning("Ouverture impossible", str(erreur), parent=self.fenetre)
			return

		# Ajout au menu et affichage des morceaux.
		self.on_playlist_created(playlist)


	def on_home(self):
		"""
		@brief Revient aux fichiers de la bibliothèque.
		"""
		# Récupération des fichiers ouverts avant la playlist.
		self.audio_files = self.fichiersBibliotheque.copy()

		# Effacement des informations du morceau précédent.
		self.selected_track = None
		self.metadata_form.clear_fields()
		self.metadata_message.set("Aucun morceau sélectionné")

		# Retour à la bibliothèque au centre.
		self.show_library()


	def on_add_track(self):
		"""
		@brief Ajoute un fichier audio à la playlist affichée.
		"""
		if self.playlist is None:
			return

		# Choix du morceau à ajouter.
		cheminFichier = filedialog.askopenfilename(parent=self.fenetre, title="Ajouter un morceau", filetypes=[("Fichiers MP3", "*.mp3"), ("Fichiers FLAC", "*.flac")])

		if cheminFichier == "":
			return

		# Vérification et ajout du morceau par le service.
		try:
			self.library_service.add_track_to_playlist(self.playlist, cheminFichier)
		except ValueError as erreur:
			messagebox.showwarning("Ajout impossible", str(erreur), parent=self.fenetre)
			return

		# Actualisation des morceaux affichés.
		self.on_open_playlist(self.playlist)


	def on_remove_track(self):
		"""
		@brief Retire le morceau sélectionné de la playlist.
		"""
		if self.playlist is None:
			return

		# Position du morceau choisi dans la liste.
		selection = self.library_view.files_list.curselection()

		if len(selection) == 0:
			messagebox.showwarning("Aucun morceau sélectionné", "Sélectionnez un morceau à retirer.", parent=self.fenetre)
			return

		# Retrait de la playlist sans supprimer le fichier audio.
		try:
			self.library_service.remove_track_from_playlist(self.playlist, selection[0])
		except IndexError:
			messagebox.showwarning("Retrait impossible", "Le morceau sélectionné n'existe plus dans la playlist.", parent=self.fenetre)
			return

		# Actualisation de la liste affichée.
		self.on_open_playlist(self.playlist)