# Vibe Generator

**Professional utility scripts for developers and teams.**

## Overview

Collection of robust, production-ready scripts for common development workflows. Designed for clarity, reliability, and ease of use.

---

## Scripts

### Vibe MP3 Cutter

**`python main.py`** - Download and cut MP3 files into segments with modular processor architecture.

#### Features

- Download MP3 from YouTube (via yt-dlp) or load local files
- Cut audio into configurable time segments (default: 8 minutes)
- Clean, modular architecture with UNIX-style composability
- Extensible processor system for future features
- Cross-platform (macOS/Linux)

#### Quick Start

```bash
# Download YouTube video and cut into 8-min segments
python main.py https://www.youtube.com/watch?v=... --cut

# Cut local MP3 into 10-min segments
python main.py ~/Music/podcast.mp3 --cut --segment-duration 600

# Download only (no cutting)
python main.py https://youtu.be/... -o ~/Music
```

#### Installation

```bash
# Requirements
brew install ffmpeg          # macOS
# or: sudo apt-get install ffmpeg  # Linux

# Install Python dependencies
pip install -r requirements.txt
```

#### Architecture

```
vibe_mp3_cutter/
├── core.py                  # Base: Downloader, Processor, Pipeline
├── downloaders/
│   ├── youtube.py          # YouTube (yt-dlp + FFmpeg)
│   └── local.py            # Local file loader
└── processors/
    ├── segment_cutter.py   # Time-based segmentation ✅
    ├── normalizer.py       # Audio normalization (stub)
    └── converter.py        # Format conversion (stub)
```

Clean separation of concerns - processors are pluggable and chainable.

#### CLI Options

```bash
usage: main.py [-h] [-o OUTPUT] [--cut] [--segment-duration DURATION] [-v] source

source                    YouTube URL or path to MP3 file
-o, --output OUTPUT       Output directory
--cut                     Enable segmentation
--segment-duration DUR    Segment duration in seconds (default: 480)
-v, --verbose            Verbose logging
```

---

### Markdown to GitHub Raw URLs

**`bin/md2raw`** - Convert local file paths in markdown reports to GitHub raw URLs.

#### Problem

AI-generated markdown reports often contain local file paths like:
```markdown
file:///Users/name/project/docs/file.md
/Users/name/project/src/component.ts
```

These links break when shared with external consultants or team members.

#### Solution

Automatically converts local paths to GitHub raw URLs for immediate external access:
```markdown
https://raw.githubusercontent.com/user/repo/main/docs/file.md
https://raw.githubusercontent.com/user/repo/main/src/component.ts
```

#### Usage

```bash
# Convert and print to stdout
bin/md2raw report.md

# Save to new file
bin/md2raw report.md external-report.md

# Edit in-place
bin/md2raw -i report.md

# Pipe from stdin
cat report.md | bin/md2raw > output.md

# Custom repository
bin/md2raw -u myuser -r myrepo -b develop input.md
```

#### Options

```
-h, --help          Show help message
-i, --in-place      Edit file in-place
-v, --verbose       Show conversion statistics
-u, --user USER     GitHub username (default: kimeisele)
-r, --repo REPO     GitHub repository (default: vibe-agency)
-b, --branch BRANCH GitHub branch (default: main)
```

#### Examples

**Basic conversion:**
```bash
bin/md2raw chat-export.md > shareable-report.md
```

**Batch processing:**
```bash
for file in reports/*.md; do
  bin/md2raw -i "$file"
done
```

**Different repository:**
```bash
export GITHUB_USER=acme
export GITHUB_REPO=project
export GITHUB_BRANCH=production

bin/md2raw internal-docs.md external-docs.md
```

#### Patterns Detected

The script handles multiple URL patterns:

1. **file:// URLs:**
   ```
   file:///Users/ss/Downloads/vibe-agency/docs/file.md
   ```

2. **Absolute paths:**
   ```
   /Users/ss/Downloads/vibe-agency/src/code.py
   ```

3. **Markdown links:**
   ```markdown
   [Architecture Docs](file:///.../vibe-agency/docs/arch.md)
   ```

4. **Plaintext references:**
   ```
   Read URL content from /path/to/vibe-agency/file.md
   ```

All are converted to:
```
https://raw.githubusercontent.com/kimeisele/vibe-agency/main/[path]
```

---

## Project Structure

```
vibe-generator/
├── bin/                    # Executable convenience wrappers
│   └── md2raw             # Main markdown converter
├── scripts/               # Implementation scripts
│   ├── markdown/          # Markdown processing
│   ├── git/              # Git utilities (planned)
│   └── utils/            # General utilities (planned)
├── examples/              # Example inputs/outputs
│   ├── input-report.md   # Example markdown with local paths
│   └── output-report.md  # Converted with GitHub raw URLs
├── test/                  # Test scripts (planned)
└── docs/                  # Additional documentation (planned)
```

---

## Design Principles

1. **Robust** - Handles edge cases gracefully, never crashes
2. **Composable** - Works with stdin/stdout for Unix pipelines
3. **Minimal Dependencies** - Pure bash + standard Unix tools
4. **Well-Documented** - Clear help text and examples
5. **Production-Ready** - Used in real workflows

---

## Installation

```bash
git clone https://github.com/kimeisele/vibe-generator.git
cd vibe-generator
chmod +x bin/*
```

Add to PATH (optional):
```bash
echo 'export PATH="$PATH:/path/to/vibe-generator/bin"' >> ~/.bashrc
source ~/.bashrc
```

---

## Requirements

- Bash 4.0+
- Standard Unix tools: `sed`, `grep`, `wc`

---

## Contributing

This project follows a philosophy of **lean, professional tooling**:

- Scripts must be robust and handle errors gracefully
- Clear documentation is mandatory
- Test with real-world examples before committing
- Minimize dependencies
- Follow existing patterns

---

## License

MIT

---

## Author

**vibe-generator** - Professional utilities for modern development workflows.

Created for teams that value reliability and simplicity.
