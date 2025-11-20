"""
Core pipeline and base classes for audio processing.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Dict, Any
import tempfile
import logging

logger = logging.getLogger(__name__)


class AudioFile:
    """Represents an audio file with metadata."""

    def __init__(self, path: str, title: str = "", duration: Optional[float] = None):
        self.path = Path(path)
        self.title = title or self.path.stem
        self.duration = duration

    def __repr__(self):
        return f"AudioFile(path={self.path}, title={self.title}, duration={self.duration})"


class Downloader(ABC):
    """Abstract base class for all downloaders."""

    @abstractmethod
    def download(self, source: str, output_dir: Optional[str] = None) -> AudioFile:
        """
        Download audio from source.

        Args:
            source: URL or file path
            output_dir: Optional output directory

        Returns:
            AudioFile object
        """
        pass

    def _get_output_dir(self, output_dir: Optional[str] = None) -> Path:
        """Get or create output directory."""
        if output_dir:
            path = Path(output_dir)
            path.mkdir(parents=True, exist_ok=True)
            return path
        return Path(tempfile.gettempdir()) / "vibe_mp3_cutter"


class Processor(ABC):
    """Abstract base class for audio processors."""

    @abstractmethod
    def process(self, audio_file: AudioFile, **kwargs) -> List[AudioFile]:
        """
        Process audio file.

        Args:
            audio_file: Input audio file
            **kwargs: Processor-specific options

        Returns:
            List of processed AudioFile objects
        """
        pass

    def validate_ffmpeg(self):
        """Check if ffmpeg is installed."""
        import shutil
        if not shutil.which("ffmpeg"):
            raise RuntimeError("ffmpeg not found. Install with: brew install ffmpeg (macOS)")


class Pipeline:
    """Orchestrates download and processing pipeline."""

    def __init__(self, downloader: Downloader):
        self.downloader = downloader
        self.processors: List[Processor] = []

    def add_processor(self, processor: Processor) -> "Pipeline":
        """Add a processor to the pipeline (fluent API)."""
        self.processors.append(processor)
        return self

    def execute(self, source: str, output_dir: Optional[str] = None, **options) -> List[AudioFile]:
        """
        Execute full pipeline: download → process.

        Args:
            source: Download source (URL or path)
            output_dir: Output directory
            **options: Options passed to processors

        Returns:
            List of final output files
        """
        logger.info(f"Starting pipeline for: {source}")

        # Download
        audio = self.downloader.download(source, output_dir)
        logger.info(f"Downloaded: {audio}")

        # Process
        current = [audio]
        for processor in self.processors:
            logger.info(f"Applying processor: {processor.__class__.__name__}")
            new_files = []
            for file in current:
                new_files.extend(processor.process(file, **options))
            current = new_files

        logger.info(f"Pipeline complete. Output files: {len(current)}")
        return current
