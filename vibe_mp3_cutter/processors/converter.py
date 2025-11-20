"""Audio format converter processor - STUB for future implementation."""

import logging
from typing import List

from vibe_mp3_cutter.core import Processor, AudioFile

logger = logging.getLogger(__name__)


class FormatConverter(Processor):
    """
    Converts audio between formats (MP3, WAV, FLAC, etc.).
    STUB: Not yet implemented.
    """

    def __init__(self, target_format: str = "mp3", bitrate: str = "192k"):
        """
        Initialize converter.

        Args:
            target_format: Target audio format (mp3, wav, flac, etc.)
            bitrate: Target bitrate (e.g., '192k', '320k')
        """
        self.target_format = target_format
        self.bitrate = bitrate

    def process(self, audio_file: AudioFile, **kwargs) -> List[AudioFile]:
        """
        Convert audio format.

        Args:
            audio_file: Input audio file
            **kwargs: Additional options

        Returns:
            List containing converted audio file
        """
        logger.info(f"[STUB] Would convert {audio_file.path} to {self.target_format} @ {self.bitrate}")
        return [audio_file]
