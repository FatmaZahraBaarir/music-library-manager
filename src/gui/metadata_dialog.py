"""
@brief Affiche le formulaire des métadonnées.
"""

import tkinter as tk

class MetadataForm:
	"""
	@brief Regroupe les champs de modification des métadonnées.
	"""

	def __init__(self, cadreMetadonnees, on_save_metadata):
		"""
		@brief Crée les champs et le bouton Enregistrer.

		@param cadreMetadonnees Cadre contenant le formulaire.
		@type cadreMetadonnees tkinter.Frame
		@param on_save_metadata Méthode qui enregistre les modifications.
		"""
		# Méthode appelée par le bouton Enregistrer.
		self.on_save_metadata = on_save_metadata

		# Champ du titre.
		self.edit_title_label = tk.Label(cadreMetadonnees, text="Modifier le titre", bg="#ffffff", fg="#1e293b")
		self.edit_title_label.pack(pady=2)

		self.title_var = tk.StringVar()
		self.title_entry = tk.Entry(cadreMetadonnees, textvariable=self.title_var, width=30, bg="#f1f5f9", fg="#1e293b")
		self.title_entry.pack(pady=2)

		# Champ de l'artiste.
		self.edit_artist_label = tk.Label(cadreMetadonnees, text="Artiste", bg="#ffffff", fg="#1e293b")
		self.edit_artist_label.pack(pady=2)

		self.artist_var = tk.StringVar()
		self.artist_entry = tk.Entry(cadreMetadonnees, textvariable=self.artist_var, width=30, bg="#f1f5f9", fg="#1e293b")
		self.artist_entry.pack(pady=2)

		# Champ de l'album.
		self.edit_album_label = tk.Label(cadreMetadonnees, text="Album", bg="#ffffff", fg="#1e293b")
		self.edit_album_label.pack(pady=2)

		self.album_var = tk.StringVar()
		self.album_entry = tk.Entry(cadreMetadonnees, textvariable=self.album_var, width=30, bg="#f1f5f9", fg="#1e293b")
		self.album_entry.pack(pady=2)

		# Champ du numéro de piste dans l'album.
		self.edit_track_number_label = tk.Label(cadreMetadonnees, text="Numéro de piste", bg="#ffffff", fg="#1e293b")
		self.edit_track_number_label.pack(pady=2)

		self.track_number_var = tk.StringVar()
		self.track_number_entry = tk.Entry(cadreMetadonnees, textvariable=self.track_number_var, width=30, bg="#f1f5f9", fg="#1e293b")
		self.track_number_entry.pack(pady=2)

		# Champ de l'année.
		self.edit_year_label = tk.Label(cadreMetadonnees, text="Année", bg="#ffffff", fg="#1e293b")
		self.edit_year_label.pack(pady=2)

		self.year_var = tk.StringVar()
		self.year_entry = tk.Entry(cadreMetadonnees, textvariable=self.year_var, width=30, bg="#f1f5f9", fg="#1e293b")
		self.year_entry.pack(pady=2)

		# Bouton de sauvegarde.
		self.save_metadata_button = tk.Button(cadreMetadonnees, text="Enregistrer les modifications", command=self.on_save_metadata)
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
		@brief Affiche les valeurs du morceau dans les champs.

		@param metadata Métadonnées du morceau.
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