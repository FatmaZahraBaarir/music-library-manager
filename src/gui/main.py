"""
@brief Lance l'interface graphique du gestionnaire musical.
"""

import tkinter as tk

from gui.main_window import MainWindow
from library.services import LibraryService

def main():
	"""
	@brief Crée la fenêtre, le service et démarre l'application.
	"""
	# Création de la fenêtre Tkinter.
	fenetre = tk.Tk()

	# Service commun pour accéder aux fonctionnalités du projet.
	library_service = LibraryService()

	# Construction de l'interface dans la fenêtre.
	interface = MainWindow(fenetre, library_service)

	# Gestion des actions de l'utilisateur.
	fenetre.mainloop()

if __name__ == "__main__":
	main()