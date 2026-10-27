class Metadata:
    """
    @brief Représente les informations descriptives d'un morceau.

    Une valeur None indique une information inconnue ou absente.
    """

    def __init__(self, title=None, artist=None, album_title=None, track_number=None, year=None):
        """
        @brief Initialise les métadonnées du morceau.

        @param title Titre du morceau, ou None.
        @type title str ou None
        @param artist Nom de l'artiste, ou None.
        @type artist str ou None
        @param album_title Titre de l'album, ou None.
        @type album_title str ou None
        @param track_number Numéro de piste, ou None.
        @type track_number int ou None
        @param year Année de publication, ou None.
        @type year int ou None
        """
        self.title = title
        self.artist = artist
        self.album_title = album_title
        self.track_number = track_number
        self.year = year
