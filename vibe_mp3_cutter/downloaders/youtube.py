"""YouTube downloader using yt-dlp and ffmpeg."""

import logging
import subprocess
from pathlib import Path
from typing import Optional

from vibe_mp3_cutter.core import Downloader, AudioFile

logger = logging.getLogger(__name__)


class YouTubeDownloader(Downloader):
    """Download MP3 from YouTube via yt-dlp."""

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
        self.validate_ffmpeg()

    def download(self, url: str, output_dir: Optional[str] = None) -> AudioFile:
        """
        Download YouTube video as MP3.

        Args:
            url: YouTube URL
            output_dir: Output directory for MP3

        Returns:
            AudioFile object
        """
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL: {url}")

        output_path = self._get_output_dir(output_dir)
        output_template = output_path / "%(title)s.%(ext)s"

        try:
            import yt_dlp
        except ImportError:
            raise ImportError("yt-dlp not installed. Install with: pip install yt-dlp")

        logger.info(f"Downloading: {url}")

        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": str(output_template),
            "quiet": False,
            "no_warnings": False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "unknown")
                duration = info.get("duration")

                # Find generated MP3
                mp3_file = output_path / f"{title}.mp3"
                if not mp3_file.exists():
                    # Try with sanitized name
                    mp3_file = list(output_path.glob("*.mp3"))[-1] if list(output_path.glob("*.mp3")) else None

                if not mp3_file or not mp3_file.exists():
                    raise RuntimeError(f"MP3 file not found after download")

                logger.info(f"Downloaded to: {mp3_file}")
                return AudioFile(str(mp3_file), title=title, duration=duration)

        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise
