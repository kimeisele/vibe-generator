"""Local file loader."""

import logging
import subprocess
from pathlib import Path
from typing import Optional

from vibe_mp3_cutter.core import Downloader, AudioFile

logger = logging.getLogger(__name__)


class LocalFileLoader(Downloader):
    """Load MP3 from local file system."""

    def __init__(self):
        self.validate_ffmpeg()

    def download(self, file_path: str, output_dir: Optional[str] = None) -> AudioFile:
        """
        Load local audio file.

        Args:
            file_path: Path to audio file
            output_dir: Ignored for local files

        Returns:
            AudioFile object
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get duration using ffprobe
        duration = self._get_duration(file_path)

        logger.info(f"Loaded: {path}")
        return AudioFile(str(path), title=path.stem, duration=duration)

    def _get_duration(self, file_path: str) -> Optional[float]:
        """Get audio duration in seconds using ffprobe."""
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1:noprint_wrappers=1",
                    file_path,
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
        except Exception as e:
            logger.warning(f"Could not determine duration: {e}")
        return None
