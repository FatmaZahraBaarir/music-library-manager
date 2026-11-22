"""
@brief Gère la fenêtre principale du gestionnaire musical.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

from gui.home_view import HomeView
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

		# Morceaux conservés lorsque l’utilisateur consulte une playlist.
		self.fichiersBibliotheque = []

		# Dossier associé aux morceaux de la bibliothèque.
		self.dossierBibliotheque = ""

		self.selected_track = None

		# Playlist actuellement affichée, ou None dans la bibliothèque.
		self.playlist = None

		# Playlists créées ou ouvertes pendant l'utilisation de l'application.
		self.playlists = []

		# Boutons associés aux playlists dans le menu de gauche.
		self.boutonsPlaylists = []

		self.fenetre.title("Gestionnaire de bibliothèque musicale")
		self.fenetre.geometry("1200x750")

		# Barre de lecture en bas.
		self.cadreLecteur = tk.Frame(self.fenetre, bg="#f1f5f9", height=90)
		self.cadreLecteur.pack(side=tk.BOTTOM, fill=tk.X)
		self.player_bar = PlayerBar(self.cadreLecteur)

		# Menu à gauche.
		self.cadreMenu = tk.Frame(self.fenetre, bg="#f1f5f9", width=200)
		self.cadreMenu.pack(side=tk.LEFT, fill=tk.Y)
		self.sidebar = Sidebar(self.cadreMenu, self.on_create_playlist, self.on_home)

		# Cadre contenant la bibliothèque et les métadonnées.
		self.cadrePrincipal = tk.Frame(self.fenetre, bg="#ffffff")
		self.cadrePrincipal.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		# Les vues seront construites lorsqu'elles seront affichées.
		self.cadreBibliotheque = None
		self.cadreMetadonnees = None
		self.metadata_form = None

		# Message utilisable même avant la création du panneau.
		self.metadata_message = tk.StringVar()
		self.metadata_message.set("Aucun morceau sélectionné")

		# Affichage de la page de bienvenue au démarrage.
		self.on_home()

	def create_metadata_panel(self):
		"""@brief Construit le panneau utilisé dans les vues de morceaux."""
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
		self.metadata_message.set("Aucun morceau sélectionné")

		self.metadata_text = tk.Label(self.cadreMetadonnees, textvariable=self.metadata_message, bg="#ffffff", fg="#1e293b")
		self.metadata_text.pack(pady=5)

		# Formulaire de modification.
		self.metadata_form = MetadataForm(self.cadreMetadonnees, self.on_save_metadata)


	def update_navigation(self, vue, playlist=None):
		"""
		@brief Grise le cadre du bouton correspondant à la vue affichée.

		@param vue Vue active : accueil, creation ou playlist.
		@param playlist Playlist affichée, ou None pour les autres vues.
		"""
		# Remise des cadres à la couleur habituelle du menu.
		self.sidebar.cadreAccueil.config(bg="#f1f5f9")
		self.sidebar.cadreCreation.config(bg="#f1f5f9")

		for boutonPlaylist in self.boutonsPlaylists:
			boutonPlaylist.cadre.config(bg="#f1f5f9")

		# Mise en gris du cadre de la vue active.
		if vue == "accueil":
			self.sidebar.cadreAccueil.config(bg="#94a3b8")
		elif vue == "creation":
			self.sidebar.cadreCreation.config(bg="#94a3b8")
		elif vue == "playlist":
			for boutonPlaylist in self.boutonsPlaylists:
				if boutonPlaylist.playlist is playlist:
					boutonPlaylist.cadre.config(bg="#94a3b8")

	def on_open_file(self):
		"""@brief Affiche les fichiers audio choisis dans la bibliothèque."""
		cheminsFichiers = filedialog.askopenfilenames(parent=self.fenetre, title="Ouvrir des morceaux", filetypes=[("Fichiers audio", "*.mp3 *.flac")])

		if len(cheminsFichiers) == 0:
			return

		# Conservation des nouveaux fichiers avant leur affichage.
		self.audio_files = list(cheminsFichiers)
		self.fichiersBibliotheque = self.audio_files.copy()
		self.dossierBibliotheque = ""
		self.playlist = None
		self.selected_track = None

		# Pour un seul fichier, conservation de son dossier.
		if len(self.audio_files) == 1:
			cheminFichier = self.audio_files[0]
			position = len(cheminFichier) - 1
			while position > 0 and cheminFichier[position] != "/":
				position -= 1

			self.dossierBibliotheque = cheminFichier[:position + 1]

		# La méthode commune remplit la liste une seule fois.
		self.show_library()

		if len(self.audio_files) > 1:
			self.library_view.directory_label.config(text=str(len(self.audio_files)) + " morceaux sélectionnés")

		self.metadata_message.set("Aucun morceau sélectionné")
		if self.metadata_form is not None:
			self.metadata_form.clear_fields()

	def on_open_folder(self):
		"""
		@brief Affiche les fichiers audio du dossier choisi.
		"""
		cheminDossier = filedialog.askdirectory(parent=self.fenetre, title="Choisir un dossier de musique")

		if cheminDossier == "":
			return

		# Recherche des fichiers MP3 et FLAC dans le dossier.
		try:
			fichiersAudio = self.library_service.find_audio_files(cheminDossier)
		except ValueError as erreur:
			messagebox.showwarning("Dossier inaccessible", str(erreur), parent=self.fenetre)
			return

		# Conservation des nouvelles données avant leur affichage.
		self.audio_files = fichiersAudio
		self.fichiersBibliotheque = self.audio_files.copy()
		self.dossierBibliotheque = cheminDossier
		self.playlist = None
		self.selected_track = None

		# La méthode commune remplit la liste et affiche le dossier.
		self.show_library()

		if self.metadata_form is not None:
			self.metadata_form.clear_fields()
		self.metadata_message.set("Aucun morceau sélectionné")

		# Message visible même lorsque le panneau des métadonnées est absent.
		if len(self.audio_files) == 0:
			messagebox.showinfo("Aucun morceau", "Aucun fichier MP3 ou FLAC reconnu dans ce dossier.", parent=self.fenetre)
	def on_file_selected(self):
		"""
		@brief Remplit le formulaire avec les informations du morceau choisi.
		"""
		# Position du morceau sélectionné dans la liste.
		selection = self.library_view.files_list.curselection()

		if len(selection) == 0:
			return

		cheminFichier = self.audio_files[selection[0]]

		# Création du panneau lors de la première demande de métadonnées.
		if self.cadreMetadonnees is None:
			self.create_metadata_panel()

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

		# Mise à jour et affichage des métadonnées sauvegardées puis relues.
		self.selected_track.metadata = metadata
		self.metadata_form.display_metadata(metadata)
		self.metadata_message.set("Métadonnées enregistrées.")

	def on_create_playlist(self):
		"""
		@brief Affiche le formulaire de création au centre.
		"""
		# Remplacement de la bibliothèque par le formulaire.
		self.cadreBibliotheque.destroy()
		if self.cadreMetadonnees is None:
			self.create_metadata_panel()

		self.cadreBibliotheque = tk.Frame(self.cadrePrincipal, bg="#ffffff")
		self.cadreBibliotheque.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)

		self.playlist_form = PlaylistDialog(self.cadreBibliotheque, self.library_service, self.on_playlist_created,self.on_home)
		self.update_navigation("creation")

	def show_library(self, accueil=True):
		"""
		@brief Affiche la liste des morceaux, sous l'accueil ou dans une playlist.

		@param accueil True pour afficher la bienvenue et le menu Ouvrir.
		"""
		if not accueil and self.cadreMetadonnees is None:
			self.create_metadata_panel()

		if self.cadreBibliotheque is not None:
			self.cadreBibliotheque.destroy()
		self.cadreBibliotheque = tk.Frame(self.cadrePrincipal, bg="#ffffff")
		self.cadreBibliotheque.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)

		if accueil:
			self.home_view = HomeView(self.cadreBibliotheque, self.on_open_folder, self.on_open_file, self.on_load_playlist)

		self.library_view = LibraryView(self.cadreBibliotheque, self.on_file_selected)
		if accueil:
			self.library_view.files_list.config(height=10)
			if len(self.audio_files) == 0:
				self.library_view.instructions_label.config(text="Ouvrez un dossier ou des morceaux avec le menu Ouvrir.")
			else:
				self.library_view.instructions_label.config(text="Sélectionnez un morceau, puis cliquez sur « Afficher les métadonnées ».")

		# Seul le texte affiché est raccourci ; les chemins complets restent en mémoire.
		for cheminFichier in self.audio_files:
			cheminTexte = str(cheminFichier)
			if accueil and self.dossierBibliotheque != "":
				debutChemin = len(self.dossierBibliotheque)
				if self.dossierBibliotheque[-1] != "/":
					debutChemin += 1
				nomAffiche = cheminTexte[debutChemin:]
			else:
				position = len(cheminTexte) - 1
				while position > 0 and cheminTexte[position] != "/":
					position -= 1
				nomAffiche = cheminTexte[position + 1:]
			self.library_view.files_list.insert(tk.END, nomAffiche)

		if accueil:
			if self.dossierBibliotheque != "":
				self.library_view.directory_label.config(text="Dossier : " + self.dossierBibliotheque)
			self.update_navigation("accueil")

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
		boutonPlaylist = PlaylistButton(self.sidebar.cadrePlaylists, playlist, self.on_open_playlist)
		self.boutonsPlaylists.append(boutonPlaylist)

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
		if self.metadata_form is not None:
			self.metadata_form.clear_fields()
		self.metadata_message.set("Aucun morceau sélectionné")

		# Affichage des morceaux au centre.
		self.show_library(False)

		# Dans une playlist, les boutons occupent toute la largeur.
		self.library_view.cadreBoutons.pack(fill=tk.X, padx=15, pady=5)

		self.library_view.files_label.config(text=playlist.name)
		self.library_view.instructions_label.config(text="Sélectionnez un morceau, puis cliquez sur « Afficher les métadonnées ».")

		# Menu de gestion des morceaux de la playlist.
		self.gerer_morceaux_button = tk.Menubutton(self.library_view.cadreActions, text="Gérer les morceaux ▾",relief=tk.RAISED)
		self.gerer_morceaux_button.pack(side=tk.LEFT, padx=5)

		self.menuMorceaux = tk.Menu(self.gerer_morceaux_button, tearoff=False)
		self.menuMorceaux.add_command(label="Ajouter des morceaux", command=self.on_add_track)
		self.menuMorceaux.add_command(label="Retirer le morceau sélectionné", command=self.on_remove_track)
		self.menuMorceaux.add_separator()
		self.menuMorceaux.add_command(label="Renommer la playlist", command=self.on_rename_playlist)
		self.gerer_morceaux_button.config(menu=self.menuMorceaux)

		# Enregistrement de la playlist.
		self.enregistrer_playlist_button = tk.Button(self.library_view.cadreBoutons, text="Enregistrer la playlist",command=self.on_save_playlist)
		self.enregistrer_playlist_button.pack(side=tk.RIGHT, padx=5)

		self.update_navigation("playlist", playlist)

	def on_rename_playlist(self):
		"""
		@brief Permet de modifier le nom de la playlist affichée.
		"""
		if self.playlist is None:
			return

		# Playlist concernée par cette fenêtre.
		playlist = self.playlist

		fenetreNom = tk.Toplevel(self.fenetre)
		fenetreNom.title("Renommer la playlist")

		nomVar = tk.StringVar(master=fenetreNom)
		nomVar.set(playlist.name)

		labelNom = tk.Label(fenetreNom, text="Nouveau nom de la playlist")
		labelNom.pack(padx=15, pady=10)

		champNom = tk.Entry(fenetreNom, textvariable=nomVar, width=35)
		champNom.pack(padx=15, pady=5)

		def valider_nom():
			"""Vérifie le nom saisi et actualise son affichage."""
			nouveauNom = nomVar.get().strip()

			if nouveauNom == "":
				messagebox.showwarning("Nom manquant", "Saisissez un nom pour la playlist.", parent=fenetreNom)
				return

			playlist.name = nouveauNom

			for boutonPlaylist in self.boutonsPlaylists:
				if boutonPlaylist.playlist is playlist:
					boutonPlaylist.bouton.config(text=nouveauNom)

			self.library_view.files_label.config(text=nouveauNom)
			fenetreNom.destroy()

		cadreValidation = tk.Frame(fenetreNom)
		cadreValidation.pack(padx=15, pady=10)

		boutonValider = tk.Button(cadreValidation, text="Valider", command=valider_nom)
		boutonValider.pack(side=tk.LEFT, padx=5)

		boutonAnnuler = tk.Button(cadreValidation, text="Annuler", command=fenetreNom.destroy)
		boutonAnnuler.pack(side=tk.LEFT, padx=5)

		# Attend l'affichage avant de réserver les interactions à cette fenêtre.
		fenetreNom.wait_visibility()
		fenetreNom.grab_set()


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
		"""@brief Affiche la bienvenue et retrouve les morceaux déjà ouverts."""
		self.selected_track = None
		self.playlist = None
		self.audio_files = self.fichiersBibliotheque.copy()
		if self.metadata_form is not None:
			self.metadata_form.clear_fields()
		self.metadata_message.set("Aucun morceau sélectionné")

		# Le panneau est recréé quand les métadonnées sont demandées.
		if self.cadreMetadonnees is not None:
			self.cadreMetadonnees.destroy()
			self.cadreMetadonnees = None
			self.metadata_form = None

		self.show_library()

	def on_add_track(self):
		"""
		@brief Ajoute les fichiers audio sélectionnés à la playlist.
		"""
		if self.playlist is None:
			return

		# Choix d'un ou de plusieurs morceaux.
		cheminsFichiers = filedialog.askopenfilenames(parent=self.fenetre, title="Ajouter des morceaux", filetypes=[("Fichiers audio", "*.mp3 *.flac")])

		if len(cheminsFichiers) == 0:
			return

		nombreAjoutes = 0
		nombreErreurs = 0

		# Vérification et ajout de chaque morceau.
		for cheminFichier in cheminsFichiers:
			try:
				self.library_service.add_track_to_playlist(self.playlist, cheminFichier)
			except ValueError:
				nombreErreurs += 1
			else:
				nombreAjoutes += 1

		# Actualisation de la playlist affichée.
		self.on_open_playlist(self.playlist)

		message = str(nombreAjoutes) + " morceau(x) ajouté(s)."
		if nombreErreurs > 0:
			message += "\n" + str(nombreErreurs) + " fichier(s) n'ont pas pu être lus."

		messagebox.showinfo("Ajout des morceaux", message, parent=self.fenetre)


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