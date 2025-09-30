# ChordPro Processor - Quick Reference

## Installation

```bash
# Clone repository
git clone <repo-url>
cd chordpro-processor

# Install dependencies
pip install -r requirements.txt

# Optional: Install as package
pip install -e .
```

## Basic Usage

```bash
# Interactive online mode (default)
python main.py

# Local file processing
python main.py --local /path/to/files

# With custom CSV metadata
python main.py --local /path/to/files metadata.csv

# With custom output directory
python main.py --local /path/to/files metadata.csv /output/path
```

## Common Options

```bash
# Parallel processing (5 workers)
python main.py --parallel 5

# Verbose logging
python main.py --verbose

# Save logs to file
python main.py --log-file process.log

# Custom configuration
python main.py --config my_config.yaml

# Combine options
python main.py --local /files --parallel 10 --verbose --log-file run.log
```

## Interactive Selection

When prompted, you can:

| Input | Action |
|-------|--------|
| `1,5,10-15` | Select specific songs |
| `all` | Select all songs |
| `search gospel` | Search for term |
| `q` or `quit` | Exit |

## Configuration File

Create `config.yaml`:

```yaml
# Network
connection_timeout: 30
max_retries: 3

# Output
default_chordpro_output: "processedChordPro"
default_freeshow_output: "processedFreeShow"

# Processing
fix_french_punctuation: true
deduplicate_sections: true
font_size: 100

# Colors
section_colors:
  chorus: "#f525d2"
  verse: ""
  bridge: "#f52598"
```

## Python API

### Basic Usage

```python
from config import ProcessorConfig
from processor import ChordProProcessor

# Initialize
config = ProcessorConfig()
processor = ChordProProcessor("metadata.csv", config)

# Process single file
enhanced = processor.enhance_chordpro("song.chordpro", "output/")
show = processor.generate_freeshow_file(enhanced, "shows/")
```

### Custom Configuration

```python
config = ProcessorConfig(
    connection_timeout=60,
    font_size=120,
    fix_french_punctuation=True
)
```

### Batch Processing

```python
from pathlib import Path

files = list(Path("input").glob("*.chordpro"))
for file in files:
    enhanced = processor.enhance_chordpro(str(file), "output/")
    processor.generate_freeshow_file(enhanced, "shows/")
```

## Logging

```python
import logging
from utils import setup_logging

# Setup logging
setup_logging(logging.DEBUG, "process.log")

# Use logger
logger = logging.getLogger(__name__)
logger.info("Processing started")
logger.error("An error occurred")
```

## File Structure

```
project/
├── main.py                    # Entry point
├── config.py                  # Configuration
├── processor.py               # Main logic
├── parsers.py                 # ChordPro parsing
├── network.py                 # Downloads
├── cli.py                     # Interactive UI
├── utils.py                   # Utilities
├── models.py                  # Data models
├── requirements.txt           # Dependencies
├── config.example.yaml        # Example config
└── processedChordPro/         # Output (enhanced)
    processedFreeShow/         # Output (.show files)
```

## Output Files

### Enhanced ChordPro
- Location: `processedChordPro/`
- Format: `jem001-enhanced.chordpro`
- Contains: Metadata + French punctuation fixes

### FreeShow Files
- Location: `processedFreeShow/`
- Format: `jem001.show`
- Contains: JSON for FreeShow software

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Network timeout | Increase `connection_timeout` in config |
| Memory issues | Use `--parallel 1` or process fewer files |
| Import errors | Run `pip install -r requirements.txt` |
| Encoding errors | Check file encoding (should be UTF-8) |
| No output | Enable `--verbose` flag |

## Common Tasks

### Process All Files Locally

```bash
python main.py --local ./chordpro_files
```

### Download Specific Songs

```bash
python main.py
# Then enter: 1,5,10-20
```

### Search and Process

```bash
python main.py
# Then enter: search Emmanuel
```

### Parallel Processing

```bash
python main.py --local ./files --parallel 10
```

### Custom Settings

```bash
python main.py --config custom.yaml --verbose
```

## French Punctuation Rules

The processor automatically fixes:

| Before | After |
|--------|-------|
| `Titre : Texte` | `Titre\u00A0: Texte` |
| `Question ?` | `Question\u00A0?` |
| `Wow !` | `Wow\u00A0!` |
| `« Texte »` | `«\u00A0Texte\u00A0»` |

Disable in config: `fix_french_punctuation: false`

## Testing

```bash
# Run all tests
pytest

# Specific test file
pytest test_processor.py

# With coverage
pytest --cov=.

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

## Environment Variables

```bash
# Set custom timeout
export CHORDPRO_TIMEOUT=60

# Set custom retries
export CHORDPRO_RETRIES=5
```

## Performance Tips

1. **Use parallel processing** for many files: `--parallel 10`
2. **Increase timeout** for slow networks: `connection_timeout: 60`
3. **Disable deduplication** if not needed: `deduplicate_sections: false`
4. **Use local mode** when possible (faster than downloads)

## Keyboard Shortcuts

In interactive mode:
- `Ctrl+C` - Cancel operation
- `Ctrl+D` - Exit (Unix)
- `Ctrl+Z` - Exit (Windows)

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error occurred |
| 130 | Cancelled by user (Ctrl+C) |

## Version Info

```bash
python main.py --version    # Show version
python -c "import __init__; print(__init__.__version__)"
```

## Support

- 📖 Full docs: `README.md`
- 🔄 Migration: `MIGRATION.md`
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

## License

MIT License - See LICENSE file

## Credits

- Original: JEMAF project
- Refactored: v2.0.0
- FreeShow: https://freeshow.app/

---

**Last Updated:** 2024
**Version:** 2.0.0
