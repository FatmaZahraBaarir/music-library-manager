class Playlist:
    """
    @brief Représente une collection ordonnée de morceaux.

    Un même morceau peut apparaître plusieurs fois dans la playlist.
    La lecture et la sauvegarde XSPF appartiennent aux services.
    """

    def __init__(self, name, file_path=None, tracks=None):
        """
        @brief Initialise une playlist.

        La liste fournie est copiée pour que la playlist possède sa propre
        liste. Les objets Track contenus ne sont pas copiés.

        @param name Nom de la playlist.
        @type name str
        @param file_path Chemin du fichier XSPF, ou None avant sauvegarde.
        @type file_path pathlib.Path ou None
        @param tracks Liste ordonnée des morceaux, ou None pour une liste vide.
        @type tracks list de Track ou None
        """
        self.name = name
        self.file_path = file_path
        self.tracks = [] if tracks is None else list(tracks)
