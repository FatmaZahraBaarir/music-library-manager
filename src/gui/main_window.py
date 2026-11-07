import tkinter as tk
from tkinter import filedialog, messagebox

from gui.sidebar import Sidebar
from gui.player_bar import PlayerBar
from gui.library_view import LibraryView
from gui.metadata_dialog import MetadataForm

class MainWindow:
	"""
	@brief Représente la fenêtre principale de l'application.

	Affiche les composants graphiques et utilise le service
	de bibliothèque pour accéder aux fonctionnalités métier.
	"""

	def __init__(self, root, library_service):
		"""
		@brief Initialise la fenêtre principale.

		@param root Fenêtre principale Tkinter.
		@type root tkinter.Tk
		@param library_service Service de gestion de la bibliothèque musicale.
		@type library_service LibraryService
		"""
		self.root = root
		self.library_service = library_service

		# Initialisation de la bibliothèque et du morceau sélectionné.
		self.audio_files = []
		self.selected_track = None

		self.root.title("Gestionnaire de bibliothèque musicale")

		# Définition de la taille initiale de la fenêtre.
		self.root.geometry("1300x850")

		# Création de la zone du lecteur en bas de la fenêtre.
		self.player_frame = tk.Frame(self.root, bg="#f1f5f9", height=90)
		self.player_frame.pack(side=tk.BOTTOM, fill=tk.X)

		# Construction des boutons dans la barre de lecture.
		self.player_bar = PlayerBar(self.player_frame)

		# Création du menu à gauche de la fenêtre.
		self.sidebar_frame = tk.Frame(self.root, bg="#f1f5f9", width=200)
		self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

		# Construction des boutons du menu dans leur cadre.
		self.sidebar = Sidebar(
			self.sidebar_frame,
			self.on_open_folder,
			self.on_open_file
		)

		# Création de la zone principale.
		self.content_frame = tk.Frame(self.root, bg="#ffffff")
		self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		# Création de la colonne contenant la bibliothèque musicale.
		self.library_frame = tk.Frame(self.content_frame, bg="#ffffff")
		self.library_frame.pack(
			side=tk.LEFT,
			fill=tk.BOTH,
			expand=True,
			padx=15,
			pady=10
		)

		# Création de la colonne contenant les informations du morceau.
		self.details_frame = tk.Frame(self.content_frame, bg="#ffffff")
		self.details_frame.pack(
			side=tk.RIGHT,
			fill=tk.Y,
			padx=15,
			pady=10
		)

		# Construction de la bibliothèque dans la colonne gauche.
		self.library_view = LibraryView(
			self.library_frame,
			self.on_file_selected
		)

		# Création d'une zone carrée pour la pochette, en haut du panneau.
		self.cover_canvas = tk.Canvas(
			self.details_frame,
			width=160,
			height=160,
			bg="#f1f5f9",
			highlightthickness=0
		)
		self.cover_canvas.pack(pady=10)

		# Message provisoire en attendant une image de pochette.
		self.cover_canvas.create_text(
			80,
			80,
			text="Pochette indisponible",
			fill="#475569",
			font=("Arial", 10)
		)

		# Création du titre des métadonnées dans la colonne droite.
		self.metadata_label = tk.Label(self.details_frame, text="Métadonnées du morceau")
		self.metadata_label.pack(pady=10)

		# Création du texte des informations du morceau.
		self.metadata_text = tk.Label(self.details_frame, text="Aucun morceau sélectionné")
		self.metadata_text.pack(pady=5)

		# Construction du formulaire de modification des métadonnées.
		self.metadata_form = MetadataForm(
			self.details_frame,
			self.on_save_metadata
		)

		self.metadata_label.config(bg="#ffffff", fg="#1e293b")
		self.metadata_text.config(bg="#ffffff", fg="#1e293b")

	def on_open_file(self):
		"""
		@brief Ouvre un fichier audio et le sélectionne dans la bibliothèque.
		"""
		# Demande à l'utilisateur de choisir un fichier MP3 ou FLAC.
		file_path = filedialog.askopenfilename(
			parent=self.root,
			title="Choisir un morceau",
			filetypes=[
				("Fichiers MP3", "*.mp3"),
				("Fichiers FLAC", "*.flac")
			]
		)

		# Interrompt l'action si l'utilisateur annule la sélection.
		if file_path == "":
			return

		# Remplace la bibliothèque affichée par le fichier choisi.
		self.audio_files = [file_path]
		self.library_view.files_list.delete(0, tk.END)
		self.library_view.files_list.insert(tk.END, file_path)

		# Réinitialisation des informations du morceau précédent.
		self.selected_track = None
		self.metadata_text.config(text="Aucun morceau sélectionné")

		# Effacement des saisies du morceau précédent.
		self.metadata_form.clear_fields()

		# Sélection du fichier et affichage de ses informations.
		self.library_view.files_list.selection_set(0)
		self.on_file_selected(None)

	def on_open_folder(self):
		"""
		@brief Sélectionne un dossier et affiche les fichiers audio trouvés.
		"""

		# Demande à l'utilisateur de choisir un dossier.
		directory_path = filedialog.askdirectory(parent=self.root,title="Choisir un dossier de musique")

		# Interrompt l'action si l'utilisateur annule la sélection.
		if directory_path == "":
			return

		# Recherche des fichiers audio et gestion d'une erreur d'exploration.
		try:
			audio_files = self.library_service.find_audio_files(directory_path)
		except ValueError as error:
			self.metadata_text.config(text=str(error))
			return

		# Conservation des chemins après une exploration réussie.
		self.audio_files = audio_files

		# Suppression des anciens éléments affichés.
		self.library_view.files_list.delete(0, tk.END)

		# Réinitialisation du morceau sélectionné et des informations affichées.
		self.selected_track = None
		self.metadata_text.config(text="Aucun morceau sélectionné")

		# Effacement des saisies du morceau précédent.
		self.metadata_form.clear_fields()

		# Informe l'utilisateur lorsque le dossier ne contient aucun audio reconnu.
		if len(self.audio_files) == 0:
			self.metadata_text.config(
				text="Aucun fichier MP3 ou FLAC reconnu dans ce dossier."
			)
			return

		# Affichage du chemin de chaque fichier audio.
		for file_path in self.audio_files:
			self.library_view.files_list.insert(tk.END, str(file_path))

	def on_file_selected(self, event):
		"""
		@brief Affiche les informations du morceau sélectionné.

		@param event Événement de sélection transmis par Tkinter.
		@type event tkinter.Event
		"""
		# Récupération des indices sélectionnés dans la liste.
		selection = self.library_view.files_list.curselection()

		# Interrompt l'action si aucun fichier n'est sélectionné.
		if len(selection) == 0:
			return

		# Récupération du chemin correspondant à la sélection.
		selected_path = self.audio_files[selection[0]]

		# Lecture des informations et gestion d'un fichier impossible à lire.
		try:
			self.selected_track = self.library_service.read_track(selected_path)
		except ValueError as error:
			self.selected_track = None
			self.metadata_form.clear_fields()
			self.metadata_text.config(text=str(error))
			return

		# Récupération des métadonnées du morceau sélectionné.
		metadata = self.selected_track.metadata

		# Remplissage du formulaire avec les métadonnées du morceau.
		self.metadata_form.display_metadata(metadata)

		# Conversion de la durée en minutes et secondes.
		duration = self.selected_track.duration_seconds

		if duration is None:
			duration_text = "Non renseignée"
		else:
			total_seconds = int(duration)
			minutes = total_seconds // 60
			seconds = total_seconds % 60
			duration_text = f"{minutes}:{seconds:02d}"

		# Affichage des informations qui ne sont pas modifiables.
		text = (
			f"Format : {self.selected_track.format.value.upper()}\n"
			f"Durée : {duration_text}"
		)
		self.metadata_text.config(text=text)


	def on_save_metadata(self):
		"""
		@brief Confirme et sauvegarde les métadonnées du morceau sélectionné.
		"""
		# Vérification de la présence d'un morceau sélectionné.
		if self.selected_track is None:
			self.metadata_text.config(text="Sélectionnez un morceau avant d'enregistrer.")
			return

		# Demande de confirmation avant de modifier le fichier audio.
		confirmation = messagebox.askyesno(
			"Enregistrer les métadonnées",
			"Voulez-vous enregistrer les modifications dans ce fichier audio ?",
			parent=self.root
		)

		if confirmation == False:
			return

		# Transmission des saisies au service de bibliothèque.
		try:
			metadata = self.library_service.update_metadata_from_text(
				file_path=self.selected_track.file_path,
				title_text=self.metadata_form.title_var.get(),
				artist_text=self.metadata_form.artist_var.get(),
				album_title_text=self.metadata_form.album_var.get(),
				track_number_text=self.metadata_form.track_number_var.get(),
				year_text=self.metadata_form.year_var.get()
			)
		except ValueError as error:
			self.metadata_text.config(text=str(error))
			return

		# Conservation des métadonnées enregistrées.
		self.selected_track.metadata = metadata

		# Affichage du résultat de la sauvegarde.
		self.metadata_text.config(text="Métadonnées enregistrées.")