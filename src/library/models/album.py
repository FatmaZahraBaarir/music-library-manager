class Album:
	"""
	@brief Représente un album local pouvant être enrichi par MusicBrainz.

	Les informations distantes restent facultatives afin qu'un album puisse
	d'abord être créé depuis les métadonnées d'un fichier local.
	"""

	def __init__(
		self,
		title,
		artist,
		musicbrainz_id=None,
		release_date=None,
		country=None,
		status=None,
		barcode=None,
		tracks=None,
		cover=None,
	):
		"""
		@brief Initialise les informations d'un album.

		@param title Titre de l'album.
		@type title str
		@param artist Artiste principal de l'album.
		@type artist str
		@param musicbrainz_id Identifiant de la release MusicBrainz, ou None.
		@type musicbrainz_id str ou None
		@param release_date Date de publication, ou None.
		@type release_date str ou None
		@param country Pays de publication, ou None.
		@type country str ou None
		@param status Statut de la release, ou None.
		@type status str ou None
		@param barcode Code-barres, ou None.
		@type barcode str ou None
		@param tracks Pistes décrites par MusicBrainz, ou None.
		@type tracks list de AlbumTrackInfo ou None
		@param cover Pochette retenue pour l'album, ou None.
		@type cover Cover ou None
		"""
		self.title = title
		self.artist = artist
		self.musicbrainz_id = musicbrainz_id
		self.release_date = release_date
		self.country = country
		self.status = status
		self.barcode = barcode
		self.tracks = [] if tracks is None else list(tracks)
		self.cover = cover
