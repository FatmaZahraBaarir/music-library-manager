import os
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame


class AudioPlayer:
	"""
	@brief Exécute les opérations techniques de lecture audio avec pygame.

	Le mixer est initialisé au premier chargement afin que la création des
	services n'ouvre pas immédiatement un périphérique audio.
	"""

	def __init__(self):
		"""
		@brief Initialise un lecteur sans charger de fichier.
		"""
		self.loaded_file = None

	@staticmethod
	def initialize_mixer():
		"""
		@brief Initialise le mixer audio s'il ne l'est pas encore.

		@raise ValueError Si aucun périphérique audio ne peut être initialisé.
		"""
		if pygame.mixer.get_init() is not None:
			return

		try:
			pygame.mixer.init()
		except pygame.error as error:
			raise ValueError(
				"Impossible d'initialiser le périphérique audio."
			) from error

	def load(self, file_path):
		"""
		@brief Charge un fichier MP3 ou FLAC dans le lecteur.

		@param file_path Chemin du fichier audio à charger.
		@type file_path str ou pathlib.Path
		@raise ValueError Si le fichier n'existe pas ou ne peut pas être chargé.
		"""
		path = Path(file_path)
		if not path.is_file():
			raise ValueError("Le fichier audio à lire n'existe pas.")

		self.initialize_mixer()

		try:
			pygame.mixer.music.load(str(path))
		except (OSError, pygame.error) as error:
			raise ValueError(
				"Impossible de charger le fichier audio."
			) from error

		self.loaded_file = path

	def play(self):
		"""
		@brief Démarre la lecture du fichier chargé.

		@raise ValueError Si aucun fichier n'est chargé ou si la lecture échoue.
		"""
		if self.loaded_file is None:
			raise ValueError("Aucun fichier audio n'est chargé.")

		try:
			pygame.mixer.music.play()
		except pygame.error as error:
			raise ValueError(
				"Impossible de démarrer la lecture audio."
			) from error

	def pause(self):
		"""
		@brief Met la lecture audio en pause.
		"""
		if pygame.mixer.get_init() is not None:
			pygame.mixer.music.pause()

	def resume(self):
		"""
		@brief Reprend la lecture audio mise en pause.
		"""
		if pygame.mixer.get_init() is not None:
			pygame.mixer.music.unpause()

	def stop(self):
		"""
		@brief Arrête la lecture audio en cours.
		"""
		if pygame.mixer.get_init() is not None:
			pygame.mixer.music.stop()

	def is_playing(self):
		"""
		@brief Indique si le mixer lit actuellement un fichier.

		@return True si le mixer est actif, sinon False.
		@rtype bool
		"""
		if pygame.mixer.get_init() is None:
			return False
		return bool(pygame.mixer.music.get_busy())
