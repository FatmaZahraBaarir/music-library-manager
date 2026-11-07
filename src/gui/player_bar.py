"""
@brief Composant de la barre de lecture audio.
"""

import tkinter as tk


class PlayerBar:
	"""
	@brief Regroupe les boutons de lecture audio.
	"""

	def __init__(self, parent):
		"""
		@brief Construit les boutons du lecteur.

		@param parent Cadre contenant la barre de lecture.
		@type parent tkinter.Frame
		"""
		# Création du bouton de lecture.
		self.play_button = tk.Button(parent, text="Lire")
		self.play_button.pack(side=tk.LEFT, padx=10, pady=10)

		# Création du bouton d'arrêt.
		self.stop_button = tk.Button(parent, text="Arrêter")
		self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)