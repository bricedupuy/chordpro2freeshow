"""
Utility functions for ChordPro processor
"""

import re
import os
import tempfile
import shutil
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None):
    """
    Setup logging configuration
    
    Args:
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
        log_file: Optional path to log file
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Setup file handler if requested
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        logger.info(f"Logging to file: {log_file}")


@contextmanager
def temporary_directory():
    """
    Context manager for temporary directory with proper cleanup
    
    Yields:
        Path object pointing to temporary directory
        
    Example:
        with temporary_directory() as temp_dir:
            # Use temp_dir
            pass
    """
    temp_dir = Path(tempfile.mkdtemp())
    try:
        yield temp_dir
    finally:
        try:
            shutil.rmtree(temp_dir)
        except OSError as e:
            logger.warning(f"Could not remove temporary directory {temp_dir}: {e}")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem use
    """
    # Remove any path separators
    filename = os.path.basename(filename)
    
    # Remove or replace invalid characters
    # Keep alphanumeric, dots, hyphens, and underscores
    filename = re.sub(r'[^\w\.-]', '_', filename)
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename


def normalize_chordpro_filename(filename: str) -> str:
    """
    Normalize ChordPro filename to fix common issues
    
    Examples:
        jem917_0.chordpro -> jem917.chordpro
        jem5.chordpro -> jem005.chordpro
    
    Args:
        filename: Original filename
        
    Returns:
        Normalized filename
    """
    # Remove _0 suffix before .chordpro
    filename = re.sub(r'_0\.chordpro$', '.chordpro', filename)
    
    # Ensure proper formatting: jem + padded number + .chordpro
    match = re.match(r'(jem(?:k)?)(\d+)', filename, re.IGNORECASE)
    if match:
        prefix = match.group(1).lower()
        number = match.group(2).zfill(3)
        return f"{prefix}{number}.chordpro"
    
    return filename


def extract_number_from_filename(filename: str) -> tuple:
    """
    Extract sort key from filename for natural sorting
    
    Handles both 'jem' and 'jemk' prefixes, sorting jem files before jemk files.
    
    Args:
        filename: Filename to parse
        
    Returns:
        Tuple of (prefix_priority, number) for sorting
    """
    # Handle both jem and jemk prefixes
    jem_match = re.search(r'jem(\d+)', filename, re.IGNORECASE)
    jemk_match = re.search(r'jemk(\d+)', filename, re.IGNORECASE)
    
    if jemk_match:
        return (1, int(jemk_match.group(1)))  # jemk files second
    elif jem_match:
        return (0, int(jem_match.group(1)))  # jem files first
    else:
        return (2, 0)  # other files last


class FrenchPunctuationHandler:
    """Handles French punctuation rules with non-breaking spaces"""
    
    # Non-breaking space character (Unicode U+00A0)
    NBSP = '\u00A0'
    
    # French double punctuation marks that require a non-breaking space
    DOUBLE_PUNCT_PATTERN = re.compile(r'\s*([;:!?»])')
    OPENING_GUILLEMETS_PATTERN = re.compile(r'(«)\s*')
    
    @classmethod
    def fix_french_punctuation(cls, text: str) -> str:
        """
        Fix French punctuation by replacing regular spaces with non-breaking spaces
        before double punctuation marks (;:!?») and after opening guillemets («).
        
        Args:
            text: Input text to process
            
        Returns:
            Text with proper French punctuation spacing
        """
        if not text or not isinstance(text, str):
            return text
        
        # Handle double punctuation: replace space before ;:!?» with non-breaking space
        text = cls.DOUBLE_PUNCT_PATTERN.sub(rf'{cls.NBSP}\1', text)
        
        # Handle opening guillemets: replace space after « with non-breaking space
        text = cls.OPENING_GUILLEMETS_PATTERN.sub(rf'\1{cls.NBSP}', text)
        
        return text


def validate_freeshow_data(data: dict) -> bool:
    """
    Validate FreeShow data structure
    
    Args:
        data: FreeShow show data to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If data structure is invalid
    """
    if not isinstance(data, list) or len(data) != 2:
        raise ValueError("FreeShow data must be a list with 2 elements [id, show_data]")
    
    show_id, show_data = data
    
    if not isinstance(show_id, str):
        raise ValueError("Show ID must be a string")
    
    if not isinstance(show_data, dict):
        raise ValueError("Show data must be a dictionary")
    
    required_fields = ['name', 'category', 'settings', 'slides', 'layouts', 'timestamps']
    missing_fields = [field for field in required_fields if field not in show_data]
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    return True


def extract_year_from_copyright(copyright_text: str) -> Optional[str]:
    """
    Extract year from copyright text
    
    Args:
        copyright_text: Copyright string
        
    Returns:
        Year as string or None if not found
    """
    year_match = re.search(r'(\d{4})', copyright_text)
    return year_match.group(1) if year_match else None


def clean_csv_row(row: dict) -> dict:
    """
    Clean CSV row by stripping whitespace from all fields
    
    Args:
        row: Dictionary of CSV row data
        
    Returns:
        Cleaned dictionary
    """
    return {
        k.strip(): v.strip() if v else '' 
        for k, v in row.items()
    }