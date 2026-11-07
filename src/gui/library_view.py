"""
@brief Affichage de la bibliothèque musicale pour la version 1.
"""

import tkinter as tk


class LibraryView:
	"""
	@brief Affiche les noms des fichiers audio disponibles.
	"""

	def __init__(self, parent, on_file_selected):
		"""
		@brief Construit la liste des morceaux.

		@param parent Cadre contenant la bibliothèque.
		@type parent tkinter.Frame
		@param on_file_selected Méthode appelée à la sélection d'un morceau.
		@type on_file_selected callable
		"""
		# Création du titre de la bibliothèque.
		self.files_label = tk.Label(
			parent,
			text="Musiques",
			font=("Arial", 14),
			bg="#ffffff",
			fg="#1e293b"
		)
		self.files_label.pack(padx=15, pady=10)

		# Affichage des instructions d'utilisation.
		self.instructions_label = tk.Label(
			parent,
			text="Ouvrez un dossier ou un fichier,\npuis sélectionnez un morceau.",
			bg="#ffffff",
			fg="#475569"
		)
		self.instructions_label.pack(padx=15, pady=10)

		# Création de la liste des morceaux.
		self.files_list = tk.Listbox(
			parent,
			width=35,
			height=12,
			bg="#f1f5f9",
			fg="#1e293b",
			selectbackground="#1d4ed8",
			selectforeground="white"
		)
		self.files_list.pack(
			fill=tk.BOTH,
			expand=True,
			padx=15,
			pady=10
		)

		# Affichage des informations lors de la sélection d'un morceau.
		self.files_list.bind("<<ListboxSelect>>", on_file_selected)