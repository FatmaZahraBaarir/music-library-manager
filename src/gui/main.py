"""
@brief Lance l'interface graphique du gestionnaire musical.
"""

import tkinter as tk
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gui.main_window import MainWindow
from library.services.library_service import LibraryService

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