"""
Vibe MP3 Cutter - Modular YouTube to MP3 Downloader with Audio Processing
Clean architecture with UNIX-style composable processors.
"""

__version__ = "1.0.0"

from vibe_mp3_cutter.core import Pipeline
from vibe_mp3_cutter.downloaders.youtube import YouTubeDownloader
from vibe_mp3_cutter.downloaders.local import LocalFileLoader
from vibe_mp3_cutter.processors.segment_cutter import SegmentCutter

__all__ = [
    "Pipeline",
    "YouTubeDownloader",
    "LocalFileLoader",
    "SegmentCutter",
]
