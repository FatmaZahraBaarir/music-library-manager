"""
@brief Point de lancement de l'interface graphique.

Ce fichier crée la fenêtre principale et démarre l'application.
"""

import tkinter as tk
from gui.main_window import MainWindow

# Création de la fenêtre principale.
root = tk.Tk()

# Création de l'interface graphique.
window = MainWindow(root)

# Démarrage de la boucle graphique.
root.mainloop()