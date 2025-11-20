#!/usr/bin/env python3
"""
Vibe MP3 Cutter - Download YouTube/MP3 and cut into segments.

Usage:
    python main.py https://www.youtube.com/watch?v=... --segment-duration 480
    python main.py ~/Music/podcast.mp3 --output ~/Downloads
    python main.py https://youtube.com/watch?v=... --cut --segment-duration 600
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List

from vibe_mp3_cutter import (
    Pipeline,
    YouTubeDownloader,
    LocalFileLoader,
    SegmentCutter,
)
from vibe_mp3_cutter.utils import validate_source, format_duration
from vibe_mp3_cutter.processors.normalizer import AudioNormalizer
from vibe_mp3_cutter.core import AudioFile

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def get_downloader(source: str):
    """Determine which downloader to use based on source."""
    if source.startswith(("http://", "https://")):
        return YouTubeDownloader()
    else:
        return LocalFileLoader()


def main():
    parser = argparse.ArgumentParser(
        description="Download and optionally cut MP3 files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download YouTube and cut into 8-min segments (default)
  %(prog)s https://www.youtube.com/watch?v=dQw4w9WgXcQ --cut

  # Download and save, no cutting
  %(prog)s https://youtu.be/dQw4w9WgXcQ -o ~/Music

  # Cut local MP3 into 10-min segments
  %(prog)s ~/Music/podcast.mp3 --cut --segment-duration 600

  # Download only (no cutting)
  %(prog)s https://www.youtube.com/watch?v=dQw4w9WgXcQ --no-cut
        """,
    )

    parser.add_argument(
        "source",
        help="YouTube URL or path to MP3 file",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output directory (default: temp directory)",
    )

    parser.add_argument(
        "--cut",
        action="store_true",
        default=False,
        help="Cut audio into segments (disabled by default)",
    )

    parser.add_argument(
        "--segment-duration",
        type=int,
        default=480,
        help="Segment duration in seconds (default: 480 = 8 minutes)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Setup verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Validate source
        source = validate_source(args.source)
        logger.info(f"Source: {source}")

        # Create pipeline
        downloader = get_downloader(source)
        pipeline = Pipeline(downloader)

        # Add processors if requested
        if args.cut:
            logger.info(f"Will cut into {args.segment_duration}s segments")
            pipeline.add_processor(SegmentCutter(segment_duration=args.segment_duration))

        # Execute pipeline
        results = pipeline.execute(source, output_dir=args.output, segment_duration=args.segment_duration)

        # Print results
        print("\n" + "=" * 60)
        print(f"Success! Generated {len(results)} file(s)")
        print("=" * 60)
        for i, file in enumerate(results, 1):
            duration_str = format_duration(file.duration) if file.duration else "unknown"
            print(f"{i:2}. {file.path.name:40} ({duration_str})")
        print("=" * 60)

        return 0

    except KeyboardInterrupt:
        logger.info("\nAborted by user")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
