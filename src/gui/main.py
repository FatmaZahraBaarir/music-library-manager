"""
@brief Point de lancement de l'interface graphique.

Ce fichier initialise le service de bibliothèque,
crée la fenêtre principale et démarre l'application.
"""

import tkinter as tk

from gui.main_window import MainWindow
from library.services import LibraryService


def main():
	"""
	@brief Initialise et démarre l'interface graphique.
	"""
	# Création de la fenêtre principale.
	root = tk.Tk()

	# Initialisation du service de bibliothèque.
	library_service = LibraryService()

	# Création de l'interface graphique.
	window = MainWindow(root, library_service)

	# Démarrage de la boucle d'événements Tkinter.
	root.mainloop()

if __name__ == "__main__":
	main()