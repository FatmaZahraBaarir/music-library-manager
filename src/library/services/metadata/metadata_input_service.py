from library.models.metadata import Metadata


class MetadataInputService:
	"""
	@brief Transforme les saisies textuelles en métadonnées métier valides.

	Une valeur None ou une chaîne vide signifie que le champ ne doit pas être
	modifié lors de la sauvegarde.
	"""

	@staticmethod
	def _normalize_optional_text(value, field_name):
		"""
		@brief Nettoie une valeur textuelle facultative.

		@param value Texte reçu du CLI ou de la GUI, ou None.
		@type value str ou None
		@param field_name Nom du champ utilisé dans le message d'erreur.
		@type field_name str
		@return Texte nettoyé ou None lorsque la saisie est vide.
		@rtype str ou None
		@raise ValueError Si la valeur n'est ni une chaîne ni None.
		"""
		if value is None:
			return None

		if not isinstance(value, str):
			raise ValueError(
				f"Le champ {field_name} doit être une chaîne de caractères."
			)

		normalized_value = value.strip()
		return normalized_value if normalized_value else None

	@classmethod
	def _parse_optional_positive_integer(cls, value, field_name):
		"""
		@brief Convertit une saisie facultative en entier strictement positif.

		@param value Texte reçu du CLI ou de la GUI, ou None.
		@type value str ou None
		@param field_name Nom du champ utilisé dans le message d'erreur.
		@type field_name str
		@return Entier strictement positif ou None.
		@rtype int ou None
		@raise ValueError Si la saisie n'est pas un entier strictement positif.
		"""
		normalized_value = cls._normalize_optional_text(value, field_name)
		if normalized_value is None:
			return None

		try:
			parsed_value = int(normalized_value)
		except ValueError as error:
			raise ValueError(
				f"Le champ {field_name} doit contenir un nombre entier."
			) from error

		if parsed_value <= 0:
			raise ValueError(
				f"Le champ {field_name} doit être strictement positif."
			)

		return parsed_value

	def create_metadata(
		self,
		title_text=None,
		artist_text=None,
		album_title_text=None,
		track_number_text=None,
		year_text=None,
	):
		"""
		@brief Construit des métadonnées depuis les textes des interfaces.

		@param title_text Titre saisi, ou None.
		@type title_text str ou None
		@param artist_text Artiste saisi, ou None.
		@type artist_text str ou None
		@param album_title_text Album saisi, ou None.
		@type album_title_text str ou None
		@param track_number_text Numéro de piste saisi, ou None.
		@type track_number_text str ou None
		@param year_text Année saisie, ou None.
		@type year_text str ou None
		@return Métadonnées nettoyées et converties.
		@rtype Metadata
		@raise ValueError Si une valeur ne respecte pas le format attendu.
		"""
		return Metadata(
			title=self._normalize_optional_text(title_text, "titre"),
			artist=self._normalize_optional_text(artist_text, "artiste"),
			album_title=self._normalize_optional_text(
				album_title_text,
				"album",
			),
			track_number=self._parse_optional_positive_integer(
				track_number_text,
				"numéro de piste",
			),
			year=self._parse_optional_positive_integer(
				year_text,
				"année",
			),
		)
