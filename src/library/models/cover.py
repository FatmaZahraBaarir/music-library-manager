class Cover:
	"""
	@brief Représente l'image de pochette d'un album.

	Cette classe conserve les données de l'image sans la télécharger
	ni l'enregistrer sur le disque.
	"""

	def __init__(self, data, mime_type, source=None, is_validated=False):
		"""
		@brief Initialise une pochette.

		@param data Contenu binaire de l'image.
		@type data bytes
		@param mime_type Type MIME de l'image, par exemple image/jpeg.
		@type mime_type str
		@param source URL ou indication de l'origine de l'image, ou None.
		@type source str ou None
		@param is_validated Indique si l'image est locale ou confirmée.
		@type is_validated bool
		"""
		self.data = data
		self.mime_type = mime_type
		self.source = source
		self.is_validated = is_validated
