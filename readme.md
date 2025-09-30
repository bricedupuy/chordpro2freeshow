# ChordPro to FreeShow Processor - Refactored

A robust Python tool for converting ChordPro format files to FreeShow presentation software format, with support for both local and online (JEMAF) resources.

## Features

- **Dual Mode Operation**: Process local files or download from JEMAF online repository
- **Enhanced Metadata**: Enriches ChordPro files with CSV metadata
- **French Punctuation**: Automatic handling of French typographic rules (non-breaking spaces)
- **Section Deduplication**: Smart deduplication of repeated song sections
- **Parallel Processing**: Process multiple files concurrently for better performance
- **Interactive Selection**: Search and select songs interactively
- **Robust Error Handling**: Comprehensive logging and retry logic
- **Configurable**: YAML/JSON configuration file support

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd chordpro-processor

# Install dependencies
pip install -r requirements.txt
```

## Project Structure

```
chordpro_processor/
├── main.py           # Entry point
├── config.py         # Configuration management
├── models.py         # Data models
├── parsers.py        # ChordPro parsing
├── processor.py      # Main processing logic
├── network.py        # Network utilities
├── cli.py            # Command-line interface
├── utils.py          # Utility functions
└── requirements.txt  # Dependencies
```

## Usage

### Interactive Online Mode (Default)

Download and process songs from JEMAF repository:

```bash
python main.py
```

This will:
1. Fetch available songs from JEMAF
2. Download metadata
3. Present an interactive selection menu
4. Process selected songs

### Local Mode

Process local ChordPro files:

```bash
# With CSV metadata
python main.py --local /path/to/chordpro/files metadata.csv

# Without CSV (will attempt online download)
python main.py --local /path/to/chordpro/files

# With custom output directory
python main.py --local /path/to/files metadata.csv /path/to/output
```

### Parallel Processing

Process multiple files concurrently:

```bash
# Process with 5 parallel workers
python main.py --parallel 5

# Local mode with parallelization
python main.py --local /path/to/files --parallel 10
```

### Advanced Options

```bash
# Verbose logging
python main.py --verbose

# Save logs to file
python main.py --log-file process.log

# Use custom configuration
python main.py --config my_config.yaml
```

## Configuration

Create a `config.yaml` file to customize behavior:

```yaml
# Network settings
jemaf_base_url: "https://jemaf.fr/ressources/chordPro/"
csv_url: "https://raw.githubusercontent.com/..."
connection_timeout: 30
max_retries: 3
retry_delay: 1.0

# Output directories
default_chordpro_output: "processedChordPro"
default_freeshow_output: "processedFreeShow"

# Processing options
fix_french_punctuation: true
deduplicate_sections: true

# FreeShow styling
font_size: 100
slide_style: "top:120px;left:50px;height:840px;width:1820px;"

# Section colors
section_colors:
  verse: ""
  chorus: "#f525d2"
  bridge: "#f52598"
  pre_chorus: "#25d2f5"
  tag: "#f5d225"
  intro: ""
  outro: ""
```

Use the configuration:

```bash
python main.py --config config.yaml
```

## Interactive Selection

When running in online mode, you can:

- **Select specific songs**: `1,5,10-15`
- **Select all songs**: `all`
- **Search by term**: `search Emmanuel`
- **Quit**: `q` or `quit`

Search looks through:
- Filenames
- Song titles
- Authors
- Composers
- Themes

## Output Files

The processor generates two types of files:

### Enhanced ChordPro Files

Located in `processedChordPro/` (by default):
- Enriched with CSV metadata
- Fixed French punctuation
- Standardized formatting
- Named: `jem001-enhanced.chordpro`

### FreeShow Files

Located in `processedFreeShow/` (by default):
- JSON format compatible with FreeShow
- Includes all metadata
- Deduplicated sections
- Proper slide formatting
- Named: `jem001.show`

## Logging

The application uses Python's logging module:

- **INFO**: Normal operation messages
- **DEBUG**: Detailed processing information (use `--verbose`)
- **WARNING**: Non-critical issues
- **ERROR**: Processing failures

Save logs to file:

```bash
python main.py --log-file processing.log --verbose
```

## Error Handling

The application handles:
- Network timeouts and retries
- Invalid file formats
- Missing metadata
- Filesystem errors
- Parallel processing failures

Failed files are logged and summarized at the end.

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## French Punctuation Rules

The processor automatically applies French typographic rules:

- Non-breaking space before: `;`, `:`, `!`, `?`, `»`
- Non-breaking space after: `«`

Example: `Titre : Texte` → `Titre\u00A0: Texte`

This can be disabled in configuration:

```yaml
fix_french_punctuation: false
```

## Troubleshooting

### Network Issues

If downloads fail:
1. Check internet connection
2. Verify URLs are accessible
3. Increase timeout: `connection_timeout: 60` in config
4. Increase retries: `max_retries: 5` in config

### Memory Issues

For large batch processing:
1. Reduce parallel workers: `--parallel 1`
2. Process in smaller batches

### Encoding Issues

Files are read with UTF-8 encoding. If issues occur:
- Check source file encoding
- Report encoding-related issues

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

[Specify your license here]

## Credits

- Original script by [Original Author]
- Refactored and enhanced version
- JEMAF repository: https://jemaf.fr/
- FreeShow: [FreeShow website]

## Support

For issues and questions:
- Open an issue on GitHub
- Check the logs with `--verbose` flag
- Review configuration settings