"""
@brief Affiche la barre de lecture en bas de la fenêtre.
"""

import tkinter as tk

class PlayerBar:
	"""
	@brief Regroupe les boutons Lire et Arrêter.
	"""

	def __init__(self, cadreLecteur):
		"""
		@brief Crée les boutons du lecteur.

		@param cadreLecteur Cadre de la barre de lecture.
		@type cadreLecteur tkinter.Frame
		"""
		# Bouton de lecture, pas encore relié au service audio.
		self.play_button = tk.Button(cadreLecteur, text="Lire - À venir")
		self.play_button.pack(side=tk.LEFT, padx=10, pady=10)

		# Bouton d'arrêt, pas encore relié au service audio.
		self.stop_button = tk.Button(cadreLecteur, text="Arrêter - À venir")
		self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)