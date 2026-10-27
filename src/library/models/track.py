from enum import Enum

from .metadata import Metadata


class AudioFormat(Enum):
    """
    @brief Énumère les formats audio pris en charge.
    """

    MP3 = "mp3"
    FLAC = "flac"


class Track:
    """
    @brief Représente un morceau associé à un fichier audio.

    Cette classe conserve les données sans ouvrir le fichier audio.
    La vérification de l'extension et du type MIME appartient aux services.
    """

    def __init__(self, file_path, format, metadata=None,
                 duration_seconds=None, lyrics=None, cover=None):
        """
        @brief Initialise un morceau et ses informations associées.

        @param file_path Chemin du fichier audio.
        @type file_path pathlib.Path
        @param format Format audio identifié.
        @type format AudioFormat
        @param metadata Métadonnées du morceau. Si None, crée un objet vide.
        @type metadata Metadata ou None
        @param duration_seconds Durée en secondes, ou None si inconnue.
        @type duration_seconds float ou None
        @param lyrics Paroles du morceau, ou None.
        @type lyrics str ou None
        @param cover Pochette associée au morceau, ou None.
        @type cover Cover ou None
        """
        self.file_path = file_path
        self.format = format
        self.metadata = Metadata() if metadata is None else metadata
        self.duration_seconds = duration_seconds
        self.lyrics = lyrics
        self.cover = cover
