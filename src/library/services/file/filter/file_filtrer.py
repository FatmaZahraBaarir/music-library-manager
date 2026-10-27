from pathlib import Path
import magic


class FileFiltrer:
   """
   @brief Vérifie l'extension et le type MIME des fichiers MP3 et FLAC.

   Cette classe ne lit pas les métadonnées. Un résultat True indique que
   l'extension et le type MIME correspondent, pas que le fichier est intact.
   """

   @staticmethod
   def has_mp3_extension(extension):
      """
      @brief Vérifie une extension MP3, sans distinguer les majuscules.

      @param extension Extension avec son point, par exemple .MP3.
      @type extension str
      @return True si l'extension correspond à .mp3, False sinon.
      @rtype bool
      """
      return extension.lower() == ".mp3"

   @staticmethod
   def has_flac_extension(extension):
      """
      @brief Vérifie une extension FLAC, sans distinguer les majuscules.

      @param extension Extension avec son point, par exemple .FLAC.
      @type extension str
      @return True si l'extension correspond à .flac, False sinon.
      @rtype bool
      """
      return extension.lower() == ".flac"

   @staticmethod
   def is_mp3_file(file_path):
      """
      @brief Vérifie qu'un fichier possède l'extension et le MIME MP3.

      @param file_path Chemin du fichier à vérifier.
      @type file_path str ou pathlib.Path
      @return False si le fichier est absent, illisible ou non conforme.
      @rtype bool
      """
      path = Path(file_path)

      try:
         if not path.is_file():
               return False

         extension = path.suffix.lower()
         if not FileFiltrer.has_mp3_extension(extension):
               return False

         mime_type = magic.from_file(str(path), mime=True)
         return mime_type == "audio/mpeg"
      except (OSError, magic.MagicException):
         return False

   @staticmethod
   def is_flac_file(file_path):
      """
      @brief Vérifie qu'un fichier possède l'extension et le MIME FLAC.

      @param file_path Chemin du fichier à vérifier.
      @type file_path str ou pathlib.Path
      @return False si le fichier est absent, illisible ou non conforme.
      @rtype bool
      """
      path = Path(file_path)

      try:
         if not path.is_file():
               return False

         extension = path.suffix.lower()
         if not FileFiltrer.has_flac_extension(extension):
               return False

         mime_type = magic.from_file(str(path), mime=True)
         return mime_type in ("audio/flac", "audio/x-flac")
      except (OSError, magic.MagicException):
         return False
