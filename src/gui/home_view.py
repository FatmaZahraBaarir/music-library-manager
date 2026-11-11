"""
@brief Affiche le message de bienvenue et le menu d’ouverture.
"""

import tkinter as tk


class HomeView:
	"""@brief Regroupe le message de bienvenue et le menu d’ouverture."""

	def __init__(self, cadreAccueil, on_open_folder, on_open_file, on_load_playlist):
		"""
		@brief Crée le message de bienvenue et le menu d'ouverture.
		@param cadreAccueil Cadre contenant la page d'accueil.
		@param on_open_folder Action d'ouverture d'un dossier.
		@param on_open_file Action d'ouverture de morceaux.
		@param on_load_playlist Action d'ouverture d'une playlist.
		"""
		self.titre_label = tk.Label(cadreAccueil, text="Bienvenue dans votre bibliothèque musicale", font=("Arial", 18, "bold"), bg="#ffffff", fg="#1e293b", wraplength=700)
		self.titre_label.pack(padx=20, pady=10)

		self.question_label = tk.Label(cadreAccueil, text="Que souhaitez-vous faire ?", font=("Arial", 14), bg="#ffffff", fg="#475569")
		self.question_label.pack(pady=5)

		self.cadreOuverture = tk.Frame(cadreAccueil, bg="#ffffff")
		self.cadreOuverture.pack(pady=5)

		# Menu permettant d'ouvrir un dossier, des morceaux ou une playlist.
		self.ouvrir_button = tk.Menubutton(self.cadreOuverture, text="Ouvrir", relief=tk.RAISED, width=28)
		self.ouvrir_button.pack(pady=5)
		self.menuOuverture = tk.Menu(self.ouvrir_button, tearoff=False)
		self.menuOuverture.add_command(label="Un dossier de musique", command=on_open_folder)
		self.menuOuverture.add_command(label="Des morceaux", command=on_open_file)
		self.menuOuverture.add_command(label="Une playlist", command=on_load_playlist)
		self.ouvrir_button.config(menu=self.menuOuverture)
