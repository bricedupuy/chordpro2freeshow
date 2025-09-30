"""
Main ChordPro processor - handles conversion to enhanced ChordPro and FreeShow formats
"""

import json
import time
import logging
import hashlib
from pathlib import Path
from typing import Dict, List

from config import ProcessorConfig
from models import SongMetadata, ChordProSection, FreeShowSlide
from parsers import MetadataLoader, ChordProParser
from utils import FrenchPunctuationHandler, extract_year_from_copyright, validate_freeshow_data

logger = logging.getLogger(__name__)


class ChordProProcessor:
    """Process ChordPro files and convert to FreeShow format"""
    
    def __init__(self, csv_file: str, config: ProcessorConfig = None):
        """
        Initialize processor
        
        Args:
            csv_file: Path to CSV metadata file
            config: ProcessorConfig instance (uses default if None)
        """
        self.config = config or ProcessorConfig()
        self.config.validate()
        
        self.metadata = MetadataLoader.load_from_csv(csv_file)
        self.parser = ChordProParser(self.config)
    
    def enhance_chordpro(self, filepath: str, output_dir: str) -> str:
        """
        Enhance a ChordPro file with metadata and French punctuation
        
        Args:
            filepath: Path to input ChordPro file
            output_dir: Directory to save enhanced file
            
        Returns:
            Path to enhanced ChordPro file
        """
        logger.debug(f"Enhancing ChordPro file: {filepath}")
        
        # Parse the original file
        file_metadata, sections = self.parser.parse_file(filepath)
        
        # Get CSV metadata
        filename = Path(filepath).stem
        lookup_key = filename.lower()
        csv_metadata = self.metadata.get(lookup_key)
        
        # Build enhanced content
        output_lines = []
        
        # Add metadata headers
        if csv_metadata:
            output_lines.append(f"{{number: {csv_metadata.number}}}")
            
            # Fix French punctuation in title
            title = csv_metadata.title
            if self.config.fix_french_punctuation:
                title = FrenchPunctuationHandler.fix_french_punctuation(title)
            output_lines.append(f"{{title: {title}}}")
            
            if csv_metadata.author:
                author = csv_metadata.author
                if self.config.fix_french_punctuation:
                    author = FrenchPunctuationHandler.fix_french_punctuation(author)
                output_lines.append(f"{{lyricist: {author}}}")
            
            if csv_metadata.composer:
                composer = csv_metadata.composer
                if self.config.fix_french_punctuation:
                    composer = FrenchPunctuationHandler.fix_french_punctuation(composer)
                output_lines.append(f"{{composer: {composer}}}")
            
            if csv_metadata.copyright:
                copyright_text = csv_metadata.copyright
                if self.config.fix_french_punctuation:
                    copyright_text = FrenchPunctuationHandler.fix_french_punctuation(copyright_text)
                output_lines.append(f"{{copyright: {copyright_text}}}")
                
                # Extract year
                year = extract_year_from_copyright(csv_metadata.copyright)
                if year:
                    output_lines.append(f"{{year: {year}}}")
        
        # Add key from original file
        if 'key' in file_metadata:
            output_lines.append(f"{{key: {file_metadata['key']}}}")
        
        output_lines.append("")
        
        # Add sections with French punctuation fixes
        for section in sections:
            output_lines.append(f"{{start_of_{section.type}}}")
            
            for line in section.content:
                # Apply French punctuation fixes to content lines (not directives)
                if self.config.fix_french_punctuation and not line.strip().startswith('{'):
                    line = FrenchPunctuationHandler.fix_french_punctuation(line)
                output_lines.append(line)
            
            output_lines.append(f"{{end_of_{section.type}}}")
            output_lines.append("")
        
        # Write enhanced file
        output_filename = f"{filename}-enhanced.chordpro"
        output_path = Path(output_dir) / output_filename
        
        output_path.write_text('\n'.join(output_lines), encoding='utf-8')
        logger.debug(f"Saved enhanced file: {output_path}")
        
        return str(output_path)
    
    def generate_freeshow_file(self, filepath: str, output_dir: str) -> str:
        """
        Generate a FreeShow .show file from enhanced ChordPro
        
        Args:
            filepath: Path to enhanced ChordPro file
            output_dir: Directory to save .show file
            
        Returns:
            Path to generated .show file
        """
        logger.debug(f"Generating FreeShow file from: {filepath}")
        
        # Parse the enhanced file
        file_metadata, sections = self.parser.parse_file(filepath)
        
        # Extract song info
        filename = Path(filepath).stem
        song_number = file_metadata.get('number', '')
        title = file_metadata.get('title', filename)
        
        # Apply French punctuation fixes
        if self.config.fix_french_punctuation:
            title = FrenchPunctuationHandler.fix_french_punctuation(title)
        
        # Generate unique IDs
        show_id = hashlib.md5(filename.encode('utf-8')).hexdigest()[:11]
        
        # Deduplicate sections if configured
        if self.config.deduplicate_sections:
            unique_sections, index_map = self.parser.deduplicate_sections(sections)
        else:
            unique_sections = sections
            index_map = list(range(len(sections)))
        
        # Create slides for unique sections
        slides = {}
        unique_slide_ids = []
        
        for i, section in enumerate(unique_sections):
            slide_id = hashlib.md5(
                f"{section.type}{i}{section.raw_content}".encode('utf-8')
            ).hexdigest()[:11]
            
            slides[slide_id] = self._create_freeshow_slide(section, slide_id)
            unique_slide_ids.append(slide_id)
        
        # Create layout based on original structure
        layout_id = hashlib.md5(f"layout{filename}".encode('utf-8')).hexdigest()[:11]
        layout_slides = [{"id": unique_slide_ids[i]} for i in index_map]
        
        # Build FreeShow data structure
        current_time = int(time.time() * 1000)
        
        # Apply French punctuation to metadata
        author = file_metadata.get('lyricist', '')
        composer = file_metadata.get('composer', '')
        copyright_text = file_metadata.get('copyright', '')
        
        if self.config.fix_french_punctuation:
            author = FrenchPunctuationHandler.fix_french_punctuation(author)
            composer = FrenchPunctuationHandler.fix_french_punctuation(composer)
            copyright_text = FrenchPunctuationHandler.fix_french_punctuation(copyright_text)
        
        # Determine category from filename
        category = "song"
        if filename.startswith('jem'):
            category = "JEM Kids" if 'jemk' in filename.lower() else "JEM"
        
        freeshow_data = [
            show_id,
            {
                "name": title,
                "origin": "jemaf",
                "private": False,
                "category": category,
                "settings": {
                    "activeLayout": layout_id,
                    "template": "default"
                },
                "timestamps": {
                    "created": current_time,
                    "modified": current_time,
                    "used": None
                },
                "quickAccess": {
                    "number": song_number
                },
                "meta": {
                    "number": song_number,
                    "title": title,
                    "artist": author,
                    "author": author,
                    "composer": composer,
                    "copyright": copyright_text,
                    "year": file_metadata.get('year', ''),
                    "key": file_metadata.get('key', '')
                },
                "slides": slides,
                "layouts": {
                    layout_id: {
                        "name": "Default",
                        "notes": "1 voix",
                        "slides": layout_slides
                    }
                },
                "media": {}
            }
        ]
        
        # Validate before saving
        try:
            validate_freeshow_data(freeshow_data)
        except ValueError as e:
            logger.warning(f"FreeShow data validation warning: {e}")
        
        # Write .show file
        output_filename = f"{Path(filename).stem.replace('-enhanced', '')}.show"
        output_path = Path(output_dir) / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(freeshow_data, f, indent=4, ensure_ascii=False)
        
        logger.debug(f"Saved FreeShow file: {output_path}")
        
        return str(output_path)
    
    def _create_freeshow_slide(self, section: ChordProSection, slide_id: str) -> Dict:
        """
        Create a FreeShow slide from a ChordPro section
        
        Args:
            section: ChordProSection to convert
            slide_id: Unique slide ID
            
        Returns:
            Dictionary in FreeShow slide format
        """
        slide_data = {
            "group": section.name,
            "color": self.config.section_colors.get(section.type, ''),
            "settings": {},
            "notes": "",
            "items": [{
                "type": "text",
                "lines": [],
                "style": self.config.slide_style,
                "align": "",
                "auto": False,
                "chords": {
                    "enabled": False
                }
            }]
        }
        
        # Add global group if applicable
        if section.type in self.config.global_groups:
            slide_data["globalGroup"] = self.config.global_groups[section.type]
        
        # Process each line in the section
        lines_data = []
        for line in section.content:
            # Skip comment lines
            if line.strip().startswith('{c:'):
                continue
            
            if line.strip():
                parsed_line = self.parser.parse_chord_line(line)
                
                # Apply French punctuation fixes
                if self.config.fix_french_punctuation:
                    parsed_line.text = FrenchPunctuationHandler.fix_french_punctuation(
                        parsed_line.text
                    )
                
                lines_data.append(parsed_line.to_freeshow_line(self.config.font_size))
        
        slide_data["items"][0]["lines"] = lines_data
        
        return slide_data
