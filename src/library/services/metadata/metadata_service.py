from library.services.file.filter.file_filtrer import FileFiltrer
from library.services.metadata.reader.metadata_reader import MetadataReader


class MetadataService:
   """
   @brief Valide le format d'un fichier et choisit le lecteur adapté.

   Le service orchestre le traitement. Il ne connaît pas les détails des
   tags ID3 ou des commentaires Vorbis.
   """

   def __init__(self, metadata_reader=None):
      """
      @brief Initialise le service de métadonnées.

      @param metadata_reader Lecteur à utiliser, ou None pour le lecteur réel.
      @type metadata_reader MetadataReader ou None
      """
      if metadata_reader is None:
         metadata_reader = MetadataReader()
      self.metadata_reader = metadata_reader

   def read_metadata(self, file_path):
      """
      @brief Valide un fichier puis extrait ses métadonnées.

      @param file_path Chemin du fichier MP3 ou FLAC.
      @type file_path str ou pathlib.Path
      @return Métadonnées extraites du fichier.
      @rtype Metadata
      @raise ValueError Si le fichier n'est ni un MP3 ni un FLAC valide.
      """
      if FileFiltrer.is_mp3_file(file_path):
         return self.metadata_reader.read_mp3(file_path)

      if FileFiltrer.is_flac_file(file_path):
         return self.metadata_reader.read_flac(file_path)

      raise ValueError(
         "Le fichier n'est pas un MP3 ou un FLAC valide."
      )
