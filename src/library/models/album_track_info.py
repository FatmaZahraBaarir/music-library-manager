class AlbumTrackInfo:
	"""
	@brief Décrit une piste d'album obtenue depuis une source distante.

	Cette classe ne représente pas un fichier local et ne possède donc ni
	chemin de fichier ni format MP3 ou FLAC.
	"""

	def __init__(
		self,
		title,
		artist=None,
		disc_number=None,
		position=None,
		duration_seconds=None,
		lyrics=None,
	):
		"""
		@brief Initialise les informations d'une piste d'album.

		@param title Titre de la piste.
		@type title str
		@param artist Artiste de la piste, ou None.
		@type artist str ou None
		@param disc_number Numéro du disque, ou None.
		@type disc_number int ou None
		@param position Position de la piste sur le disque, ou None.
		@type position int ou str ou None
		@param duration_seconds Durée en secondes, ou None.
		@type duration_seconds float ou None
		@param lyrics Paroles en texte simple ou synchronisé, ou None.
		@type lyrics str ou None
		"""
		self.title = title
		self.artist = artist
		self.disc_number = disc_number
		self.position = position
		self.duration_seconds = duration_seconds
		self.lyrics = lyrics
