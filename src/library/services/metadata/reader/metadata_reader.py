from mutagen import MutagenError
from mutagen.flac import FLAC
from mutagen.mp3 import MP3

from library.models.metadata import Metadata


class MetadataReader:
    """
    @brief Extrait les métadonnées des fichiers MP3 et FLAC déjà validés.

    Cette classe ne vérifie ni l'extension ni le type MIME. Cette validation
    appartient au MetadataService avec l'aide de FileFiltrer.
    """

    @staticmethod
    def _first_value(value):
        """
        @brief Récupère la première valeur d'un tag Mutagen.

        @param value Valeur simple, liste de valeurs ou None.
        @return Première valeur sous forme de chaîne, ou None.
        @rtype str ou None
        """
        if value is None:
            return None
        if isinstance(value, (list, tuple)):
            if not value:
                return None
            value = value[0]
        text = str(value).strip()
        return text if text else None

    @staticmethod
    def _parse_number(value):
        """
        @brief Convertit un numéro de piste comme 3/12 en entier.

        @param value Valeur du tag à convertir.
        @return Numéro extrait, ou None si la conversion échoue.
        @rtype int ou None
        """
        text = MetadataReader._first_value(value)
        if text is None:
            return None
        try:
            return int(text.split("/", 1)[0])
        except ValueError:
            return None

    @staticmethod
    def _parse_year(value):
        """
        @brief Extrait l'année d'une date ou d'un tag d'année.

        @param value Valeur du tag à convertir.
        @return Année extraite, ou None si la conversion échoue.
        @rtype int ou None
        """
        text = MetadataReader._first_value(value)
        if text is None:
            return None
        try:
            return int(text[:4])
        except ValueError:
            return None

    def read_mp3(self, file_path):
        """
        @brief Lit les tags ID3 d'un fichier MP3 validé.

        @param file_path Chemin du fichier MP3.
        @type file_path str ou pathlib.Path
        @return Métadonnées extraites du fichier.
        @rtype Metadata
        @raise ValueError Si Mutagen ne peut pas lire le fichier.
        """
        try:
            audio = MP3(file_path)
            tags = audio.tags

            if tags is None:
                return Metadata()

            return Metadata(
                title=self._first_value(tags.get("TIT2")),
                artist=self._first_value(tags.get("TPE1")),
                album_title=self._first_value(tags.get("TALB")),
                track_number=self._parse_number(tags.get("TRCK")),
                year=self._parse_year(tags.get("TDRC")),
            )
        except (MutagenError, OSError) as error:
            raise ValueError("Impossible de lire les métadonnées MP3.") from error

    def read_flac(self, file_path):
        """
        @brief Lit les commentaires Vorbis d'un fichier FLAC validé.

        @param file_path Chemin du fichier FLAC.
        @type file_path str ou pathlib.Path
        @return Métadonnées extraites du fichier.
        @rtype Metadata
        @raise ValueError Si Mutagen ne peut pas lire le fichier.
        """
        try:
            audio = FLAC(file_path)

            return Metadata(
                title=self._first_value(audio.get("title")),
                artist=self._first_value(audio.get("artist")),
                album_title=self._first_value(audio.get("album")),
                track_number=self._parse_number(audio.get("tracknumber")),
                year=self._parse_year(audio.get("date")),
            )
        except (MutagenError, OSError) as error:
            raise ValueError("Impossible de lire les métadonnées FLAC.") from error
