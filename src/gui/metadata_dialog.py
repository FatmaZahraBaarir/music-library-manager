"""
@brief Composant du formulaire de modification des métadonnées.
"""

import tkinter as tk

class MetadataForm:
	"""
	@brief Regroupe les champs de modification des métadonnées.
	"""

	def __init__(self, parent, on_save_metadata):
		"""
		@brief Construit le formulaire de modification.

		@param parent Cadre contenant le formulaire.
		@type parent tkinter.Frame
		@param on_save_metadata Méthode appelée pour enregistrer les modifications.
		@type on_save_metadata callable
		"""
		self.parent = parent
		self.on_save_metadata = on_save_metadata

		# Création du titre du champ de modification.
		self.edit_title_label = tk.Label(
			self.parent,
			text="Modifier le titre",
			bg="#ffffff",
			fg="#1e293b"
		)
		self.edit_title_label.pack(pady=2)

		# Variable de contrôle contenant le titre saisi.
		self.title_var = tk.StringVar()

		# Création du champ de saisie du titre sur fond gris clair.
		self.title_entry = tk.Entry(
			self.parent,
			textvariable=self.title_var,
			width=30,
			bg="#f1f5f9",
			fg="#1e293b"
		)
		self.title_entry.pack(pady=2)

		# Création du champ de modification de l'artiste.
		self.edit_artist_label = tk.Label(
			self.parent,
			text="Artiste",
			bg="#ffffff",
			fg="#1e293b"
		)
		self.edit_artist_label.pack(pady=2)

		self.artist_var = tk.StringVar()
		self.artist_entry = tk.Entry(
			self.parent,
			textvariable=self.artist_var,
			width=30,
			bg="#f1f5f9",
			fg="#1e293b"
		)
		self.artist_entry.pack(pady=2)

		# Création du champ de modification de l'album.
		self.edit_album_label = tk.Label(
			self.parent,
			text="Album",
			bg="#ffffff",
			fg="#1e293b"
		)
		self.edit_album_label.pack(pady=2)

		self.album_var = tk.StringVar()
		self.album_entry = tk.Entry(
			self.parent,
			textvariable=self.album_var,
			width=30,
			bg="#f1f5f9",
			fg="#1e293b"
		)
		self.album_entry.pack(pady=2)

		# Création du champ de modification du numéro de piste.
		self.edit_track_number_label = tk.Label(
			self.parent,
			text="Numéro de piste",
			bg="#ffffff",
			fg="#1e293b"
		)
		self.edit_track_number_label.pack(pady=2)

		self.track_number_var = tk.StringVar()
		self.track_number_entry = tk.Entry(
			self.parent,
			textvariable=self.track_number_var,
			width=30,
			bg="#f1f5f9",
			fg="#1e293b"
		)
		self.track_number_entry.pack(pady=2)

		# Création du champ de modification de l'année.
		self.edit_year_label = tk.Label(
			self.parent,
			text="Année",
			bg="#ffffff",
			fg="#1e293b"
		)
		self.edit_year_label.pack(pady=2)

		self.year_var = tk.StringVar()
		self.year_entry = tk.Entry(
			self.parent,
			textvariable=self.year_var,
			width=30,
			bg="#f1f5f9",
			fg="#1e293b"
		)
		self.year_entry.pack(pady=2)

		# Création du bouton de sauvegarde des métadonnées.
		self.save_metadata_button = tk.Button(
			self.parent,
			text="Enregistrer les modifications",
			command=self.on_save_metadata
		)
		self.save_metadata_button.pack(pady=5)

	def clear_fields(self):
		"""
		@brief Vide les cinq champs du formulaire.
		"""
		self.title_var.set("")
		self.artist_var.set("")
		self.album_var.set("")
		self.track_number_var.set("")
		self.year_var.set("")

	def display_metadata(self, metadata):
		"""
		@brief Remplit les champs avec les métadonnées du morceau.

		@param metadata Métadonnées à afficher dans le formulaire.
		@type metadata Metadata
		"""
		# Effacement des valeurs du morceau précédent.
		self.clear_fields()

		# Remplissage des champs dont les valeurs sont connues.
		if metadata.title != None:
			self.title_var.set(metadata.title)

		if metadata.artist != None:
			self.artist_var.set(metadata.artist)

		if metadata.album_title != None:
			self.album_var.set(metadata.album_title)

		if metadata.track_number != None:
			self.track_number_var.set(str(metadata.track_number))

		if metadata.year != None:
			self.year_var.set(str(metadata.year))