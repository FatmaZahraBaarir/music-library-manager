"""
@brief Affiche la bibliothèque musicale.
"""

import tkinter as tk

class LibraryView:
	"""
	@brief Affiche les fichiers audio et permet de choisir un morceau.
	"""

	def __init__(self, cadreBibliotheque, on_file_selected):
		"""
		@brief Crée la liste des fichiers et le bouton d'affichage.

		@param cadreBibliotheque Cadre contenant les fichiers audio.
		@type cadreBibliotheque tkinter.Frame
		@param on_file_selected Méthode qui affiche les métadonnées.
		"""
		# Création du titre de la bibliothèque.
		self.files_label = tk.Label(cadreBibliotheque, text="Musiques", font=("Arial", 14), bg="#ffffff", fg="#1e293b")
		self.files_label.pack(padx=15, pady=10)

		# Affichage des instructions.
		self.instructions_label = tk.Label(cadreBibliotheque, text="Ouvrez un dossier ou un fichier.\nSélectionnez un morceau, puis cliquez sur « Afficher les métadonnées ».", bg="#ffffff", fg="#475569")
		self.instructions_label.pack(padx=15, pady=10)

		# Ligne réservée au menu de gestion des morceaux de la playlist.
		self.cadreActions = tk.Frame(cadreBibliotheque, bg="#ffffff")
		self.cadreActions.pack(fill=tk.X, padx=15, pady=5)

		# Création de la liste des fichiers audio.
		self.files_list = tk.Listbox(cadreBibliotheque, width=65, height=20, bg="#f1f5f9", fg="#1e293b", selectbackground="#1d4ed8")
		self.files_list.pack( padx=15, pady=10)

		# Affichage du dossier ouvert.
		self.directory_label = tk.Label(cadreBibliotheque, text="", bg="#ffffff", fg="#475569", justify=tk.LEFT)
		self.directory_label.pack(padx=15, pady=5)

		# Méthode de la fenêtre principale utilisée pour afficher les informations.
		self.on_file_selected = on_file_selected

		# Ligne contenant les boutons sous la liste.
		self.cadreBoutons = tk.Frame(cadreBibliotheque, bg="#ffffff")
		self.cadreBoutons.pack(padx=15, pady=5)

		# Création du bouton d'affichage des métadonnées.
		self.show_metadata_button = tk.Button(self.cadreBoutons, text="Afficher les métadonnées",command=self.show_selected_metadata)
		self.show_metadata_button.pack(side=tk.LEFT, padx=5)


	def show_selected_metadata(self):
		"""
		@brief Demande l'affichage des métadonnées du morceau sélectionné.
		"""
		# Appel de la méthode fournie par la fenêtre principale.
		self.on_file_selected()