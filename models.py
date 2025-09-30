"""
Data models for ChordPro processor
"""

from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class SongMetadata:
    """Song metadata from CSV file"""
    number: str
    title: str
    title2: str
    original_title: str
    composer: str
    author: str
    key: str
    format: str
    copyright: str
    reference: str
    theme: str
    tune_of: str
    volume: str
    supplement: str
    f1: str
    link: str
    
    def __post_init__(self):
        """Clean and validate fields after initialization"""
        # Strip whitespace from all string fields
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            if isinstance(value, str):
                setattr(self, field_name, value.strip())


@dataclass
class ChordProSection:
    """Represents a section in a ChordPro file"""
    name: str  # e.g., "Strophe 1", "Refrain", "Pont"
    type: str  # verse, chorus, bridge, etc.
    number: Optional[str]
    content: List[str]
    raw_content: str
    
    def get_content_hash(self) -> str:
        """
        Get hash of content for deduplication (excludes comments)
        
        Returns:
            MD5 hash of content lines (excluding comments)
        """
        import hashlib
        
        # Filter out comment lines for content comparison
        content_lines = [
            line for line in self.content 
            if not line.strip().startswith('{c:')
        ]
        content_str = '\n'.join(content_lines)
        return hashlib.md5(content_str.encode('utf-8')).hexdigest()


@dataclass
class FreeShowSlide:
    """Represents a slide in FreeShow format"""
    slide_id: str
    group: str
    color: str
    global_group: str
    lines: List[Dict]
    settings: Dict = None
    notes: str = ""
    
    def __post_init__(self):
        if self.settings is None:
            self.settings = {}
    
    def to_dict(self) -> Dict:
        """Convert to FreeShow slide dictionary format"""
        slide_data = {
            "group": self.group,
            "color": self.color,
            "settings": self.settings,
            "notes": self.notes,
            "items": [{
                "type": "text",
                "lines": self.lines,
                "style": "top:120px;left:50px;height:840px;width:1820px;",
                "align": "",
                "auto": False,
                "chords": {
                    "enabled": False
                }
            }]
        }
        
        if self.global_group:
            slide_data["globalGroup"] = self.global_group
        
        return slide_data


@dataclass
class ProcessedFile:
    """Information about a processed file"""
    original: str
    enhanced: str
    show: str
    
    def get_title(self) -> Optional[str]:
        """
        Extract title from enhanced ChordPro file
        
        Returns:
            Song title or None if not found
        """
        import re
        
        try:
            with open(self.enhanced, 'r', encoding='utf-8') as f:
                content = f.read()
                title_match = re.search(r'\{title:\s*([^}]+)\}', content)
                return title_match.group(1) if title_match else None
        except Exception:
            return None


@dataclass
class ChordPosition:
    """Represents a chord position in a line"""
    id: str
    pos: int
    key: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format for FreeShow"""
        return {
            'id': self.id,
            'pos': self.pos,
            'key': self.key
        }


@dataclass
class ParsedLine:
    """Represents a parsed line with chords and text"""
    text: str
    chords: List[ChordPosition]
    
    def to_freeshow_line(self, font_size: int = 100) -> Dict:
        """
        Convert to FreeShow line format
        
        Args:
            font_size: Font size for the line
            
        Returns:
            Dictionary in FreeShow line format
        """
        return {
            "align": "",
            "text": [{
                "value": self.text,
                "style": f"font-size: {font_size}px;"
            }],
            "chords": [chord.to_dict() for chord in self.chords]
        }
