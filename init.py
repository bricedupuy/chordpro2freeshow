"""
ChordPro to FreeShow Processor

A robust Python package for converting ChordPro format files to FreeShow 
presentation software format, with support for both local and online resources.
"""

__version__ = "2.0.0"
__author__ = "ChordPro Processor Team"
__license__ = "MIT"

from .config import ProcessorConfig
from .models import SongMetadata, ChordProSection, ProcessedFile
from .processor import ChordProProcessor
from .parsers import ChordProParser, MetadataLoader
from .network import OnlineResourceManager
from .utils import (
    FrenchPunctuationHandler,
    sanitize_filename,
    normalize_chordpro_filename,
    extract_number_from_filename
)

__all__ = [
    # Main classes
    "ChordProProcessor",
    "ProcessorConfig",
    
    # Data models
    "SongMetadata",
    "ChordProSection",
    "ProcessedFile",
    
    # Parsers
    "ChordProParser",
    "MetadataLoader",
    
    # Network
    "OnlineResourceManager",
    
    # Utils
    "FrenchPunctuationHandler",
    "sanitize_filename",
    "normalize_chordpro_filename",
    "extract_number_from_filename",
]
