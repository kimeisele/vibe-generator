"""Audio normalizer processor - STUB for future implementation."""

import logging
from typing import List

from vibe_mp3_cutter.core import Processor, AudioFile

logger = logging.getLogger(__name__)


class AudioNormalizer(Processor):
    """
    Normalizes audio levels to standard loudness.
    STUB: Not yet implemented.
    """

    def __init__(self, target_loudness: float = -16.0):
        """
        Initialize normalizer.

        Args:
            target_loudness: Target loudness in LUFS (default: -16.0)
        """
        self.target_loudness = target_loudness

    def process(self, audio_file: AudioFile, **kwargs) -> List[AudioFile]:
        """
        Normalize audio levels.

        Args:
            audio_file: Input audio file
            **kwargs: Additional options

        Returns:
            List containing normalized audio file
        """
        logger.info(f"[STUB] Would normalize {audio_file.path} to {self.target_loudness} LUFS")
        return [audio_file]
