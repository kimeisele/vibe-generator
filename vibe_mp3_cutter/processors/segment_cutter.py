"""Audio segmentation processor - cuts audio into time-based segments."""

import logging
import subprocess
from pathlib import Path
from typing import List, Optional

from vibe_mp3_cutter.core import Processor, AudioFile

logger = logging.getLogger(__name__)


class SegmentCutter(Processor):
    """
    Cuts audio into segments of fixed duration.

    Default: 8 minutes (480 seconds) - can be overridden.
    Uses ffmpeg for robust cross-platform audio cutting.
    """

    def __init__(self, segment_duration: int = 480, ffmpeg_path: str = "ffmpeg"):
        """
        Initialize segment cutter.

        Args:
            segment_duration: Segment duration in seconds (default: 480 = 8 min)
            ffmpeg_path: Path to ffmpeg binary
        """
        self.segment_duration = segment_duration
        self.ffmpeg_path = ffmpeg_path
        self.validate_ffmpeg()

    def process(self, audio_file: AudioFile, segment_duration: Optional[int] = None, **kwargs) -> List[AudioFile]:
        """
        Cut audio into segments.

        Args:
            audio_file: Input audio file
            segment_duration: Override default segment duration (seconds)
            **kwargs: Additional options (ignored)

        Returns:
            List of segment AudioFile objects
        """
        duration = segment_duration or self.segment_duration

        logger.info(f"Cutting {audio_file.path} into {duration}s segments")

        # Get audio duration if not available
        if audio_file.duration is None:
            audio_file.duration = self._get_duration(str(audio_file.path))

        if audio_file.duration is None:
            logger.warning(f"Could not determine duration of {audio_file.path}, skipping")
            return [audio_file]

        # Generate segments
        segments = []
        segment_count = int(audio_file.duration / duration) + (1 if audio_file.duration % duration > 0 else 0)

        for i in range(segment_count):
            start_time = i * duration
            segments.append((i, start_time))

        # Cut segments using ffmpeg
        output_files = []
        for segment_num, start_time in segments:
            output_file = self._cut_segment(audio_file, segment_num, start_time, duration)
            if output_file:
                output_files.append(output_file)

        logger.info(f"Created {len(output_files)} segments")
        return output_files

    def _cut_segment(self, audio_file: AudioFile, segment_num: int, start_time: int, duration: int) -> Optional[AudioFile]:
        """
        Cut a single segment from audio file.

        Args:
            audio_file: Source audio file
            segment_num: Segment number (0-indexed)
            start_time: Start time in seconds
            duration: Segment duration in seconds

        Returns:
            AudioFile for the segment, or None if cutting failed
        """
        output_path = audio_file.path.parent / f"{audio_file.title}_segment_{segment_num:03d}.mp3"

        cmd = [
            self.ffmpeg_path,
            "-i",
            str(audio_file.path),
            "-ss",
            str(start_time),
            "-t",
            str(duration),
            "-c",
            "copy",  # Copy codec (fast, no re-encoding)
            "-y",  # Overwrite output
            str(output_path),
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                logger.error(f"FFmpeg error for segment {segment_num}: {result.stderr}")
                return None

            logger.debug(f"Created segment: {output_path}")
            return AudioFile(str(output_path), title=f"{audio_file.title}_segment_{segment_num:03d}")

        except subprocess.TimeoutExpired:
            logger.error(f"Segment {segment_num} cutting timed out")
            return None
        except Exception as e:
            logger.error(f"Error cutting segment {segment_num}: {e}")
            return None

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
