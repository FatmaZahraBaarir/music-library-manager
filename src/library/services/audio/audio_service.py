from library.models.playlist import Playlist
from library.models.track import Track
from library.services.audio.player.audio_player import AudioPlayer


class AudioService:
	"""
	@brief Orchestre la lecture des morceaux et des playlists.

	Le service conserve le morceau courant et délègue les opérations techniques
	à AudioPlayer. Le CLI ou la GUI appelle update_playlist_playback()
	régulièrement pour passer au morceau suivant sans créer de thread secondaire.
	"""

	def __init__(self, audio_player=None):
		"""
		@brief Initialise le service audio.

		@param audio_player Lecteur à utiliser, ou None pour le lecteur réel.
		@type audio_player AudioPlayer ou None
		"""
		if audio_player is None:
			audio_player = AudioPlayer()

		self.audio_player = audio_player
		self.current_track = None
		self.current_playlist = None
		self.current_track_index = None
		self.is_paused = False

	@staticmethod
	def validate_track(track):
		"""
		@brief Vérifie qu'une valeur est un morceau exploitable.

		@param track Morceau à vérifier.
		@type track Track
		@raise ValueError Si la valeur n'est pas un Track.
		"""
		if not isinstance(track, Track):
			raise ValueError("La lecture audio attend un objet Track.")

	def start_track(self, track):
		"""
		@brief Charge et démarre un morceau déjà validé.

		@param track Morceau à démarrer.
		@type track Track
		"""
		self.validate_track(track)
		self.audio_player.stop()
		self.audio_player.load(track.file_path)
		self.audio_player.play()
		self.current_track = track
		self.is_paused = False

	def play_track(self, track):
		"""
		@brief Lit un morceau et abandonne une éventuelle playlist en cours.

		@param track Morceau à lire.
		@type track Track
		@return Morceau dont la lecture a démarré.
		@rtype Track
		"""
		self.validate_track(track)
		self.current_playlist = None
		self.current_track_index = None
		self.start_track(track)
		return track

	def play_playlist(self, playlist):
		"""
		@brief Démarre le premier morceau d'une playlist.

		Le CLI ou la GUI doit ensuite appeler update_playlist_playback()
		régulièrement afin de passer au morceau suivant.

		@param playlist Playlist à lire.
		@type playlist Playlist
		@return Premier morceau dont la lecture a démarré.
		@rtype Track
		@raise ValueError Si la playlist est invalide ou vide.
		"""
		if not isinstance(playlist, Playlist):
			raise ValueError("La lecture attend un objet Playlist.")
		if not playlist.tracks:
			raise ValueError("Impossible de lire une playlist vide.")
		for track in playlist.tracks:
			self.validate_track(track)

		self.current_playlist = playlist
		self.current_track_index = 0
		self.start_track(playlist.tracks[0])
		return playlist.tracks[0]

	def update_playlist_playback(self):
		"""
		@brief Passe au morceau suivant lorsque le morceau courant est terminé.

		Cette méthode ne bloque pas. Elle doit être appelée périodiquement par
		le thread principal du CLI ou de la GUI.

		@return Morceau courant, ou None lorsque la playlist est terminée.
		@rtype Track ou None
		"""
		if self.current_playlist is None:
			return self.current_track

		if self.is_paused or self.audio_player.is_playing():
			return self.current_track

		if self.current_track_index is None:
			raise ValueError("La position dans la playlist est inconnue.")

		next_index = self.current_track_index + 1
		if next_index >= len(self.current_playlist.tracks):
			self.current_track = None
			self.current_playlist = None
			self.current_track_index = None
			self.is_paused = False
			return None

		self.current_track_index = next_index
		self.start_track(self.current_playlist.tracks[next_index])
		return self.current_track

	def pause_playback(self):
		"""
		@brief Met la lecture courante en pause.

		@raise ValueError Si aucun morceau n'est en cours.
		"""
		if self.current_track is None:
			raise ValueError("Aucun morceau n'est en cours de lecture.")
		if self.is_paused:
			return
		self.audio_player.pause()
		self.is_paused = True

	def resume_playback(self):
		"""
		@brief Reprend la lecture mise en pause.

		@raise ValueError Si aucun morceau n'est en cours.
		"""
		if self.current_track is None:
			raise ValueError("Aucun morceau n'est en cours de lecture.")
		if not self.is_paused:
			return
		self.audio_player.resume()
		self.is_paused = False

	def stop_playback(self):
		"""
		@brief Arrête le morceau ou la playlist en cours.
		"""
		self.audio_player.stop()
		self.current_track = None
		self.current_playlist = None
		self.current_track_index = None
		self.is_paused = False

	def is_playing(self):
		"""
		@brief Indique si un morceau est actuellement lu sans être en pause.

		@return True pendant une lecture active, sinon False.
		@rtype bool
		"""
		return (
			self.current_track is not None
			and not self.is_paused
			and self.audio_player.is_playing()
		)
