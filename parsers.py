"""
ChordPro file parsing utilities
"""

import re
import csv
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from models import SongMetadata, ChordProSection, ChordPosition, ParsedLine
from config import ProcessorConfig
from utils import clean_csv_row

logger = logging.getLogger(__name__)


class MetadataLoader:
    """Load and manage song metadata from CSV"""
    
    @staticmethod
    def load_from_csv(csv_file: str) -> Dict[str, SongMetadata]:
        """
        Load song metadata from CSV file
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            Dictionary mapping filename (lowercase) to SongMetadata
        """
        metadata = {}
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Remove BOM if present
                if content.startswith('\ufeff'):
                    content = content[1:]
                
                reader = csv.DictReader(content.splitlines(), delimiter=';')
                
                for row in reader:
                    clean_row = clean_csv_row(row)
                    
                    fichier = clean_row.get('Fichier')
                    if not fichier:
                        continue
                    
                    # Use lowercase filename as lookup key for case-insensitive matching
                    key = fichier.lower()
                    
                    metadata[key] = SongMetadata(
                        number=fichier,
                        title=clean_row.get('Titre', ''),
                        title2=clean_row.get('2e titre', ''),
                        original_title=clean_row.get('Titre original', ''),
                        composer=clean_row.get('Compositeur', ''),
                        author=clean_row.get('Auteur', ''),
                        key=clean_row.get('Tonalité', ''),
                        format=clean_row.get('Format', ''),
                        copyright=clean_row.get('Copyright', ''),
                        reference=clean_row.get('Référence', ''),
                        theme=clean_row.get('Thème', ''),
                        tune_of=clean_row.get('Air du', ''),
                        volume=clean_row.get('Vol.', ''),
                        supplement=clean_row.get('Suppl', ''),
                        f1=clean_row.get('F1', ''),
                        link=clean_row.get('Lien', '')
                    )
                    
            logger.info(f"Loaded metadata for {len(metadata)} songs from {csv_file}")
            
        except Exception as e:
            logger.error(f"Error loading metadata from {csv_file}: {e}")
        
        return metadata


class ChordProParser:
    """Parse ChordPro files"""
    
    def __init__(self, config: ProcessorConfig):
        """
        Initialize parser
        
        Args:
            config: ProcessorConfig instance
        """
        self.config = config
        self.chord_pattern = re.compile(r'\[([^\]]+)\]')
    
    def parse_file(self, filepath: str) -> Tuple[Dict, List[ChordProSection]]:
        """
        Parse a ChordPro file and extract metadata and sections
        
        Args:
            filepath: Path to ChordPro file
            
        Returns:
            Tuple of (metadata dict, list of ChordProSection objects)
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = {}
        sections = []
        
        current_section_label = None
        current_section_content = []
        current_section_info = None
        in_section = False
        
        lines = content.split('\n')
        
        for line in lines:
            stripped_line = line.strip()
            
            # Handle section labels (comments)
            if stripped_line.startswith('{c:'):
                current_section_label = stripped_line[3:-1].strip()
                if in_section:
                    current_section_content.append(line)
            
            # Handle start of section
            elif stripped_line.startswith('{start_of_'):
                # End previous section if needed
                if in_section and current_section_info:
                    sections.append(self._create_section(
                        current_section_info,
                        current_section_content
                    ))
                
                in_section = True
                block_type = stripped_line[10:-1].strip()
                
                current_section_info = self._parse_section_info(
                    block_type,
                    current_section_label
                )
                current_section_label = None
                current_section_content = []
            
            # Handle end of section
            elif stripped_line.startswith('{end_of_'):
                if in_section and current_section_info:
                    sections.append(self._create_section(
                        current_section_info,
                        current_section_content
                    ))
                    in_section = False
                    current_section_info = None
                    current_section_content = []
            
            # Handle directives
            elif stripped_line.startswith('{'):
                directive_match = re.match(r'\{([^:]+)(?::(.*))?\}', stripped_line)
                if directive_match:
                    key = directive_match.group(1).strip()
                    value = directive_match.group(2).strip() if directive_match.group(2) else ''
                    metadata[key] = value
                
                if in_section:
                    current_section_content.append(line)
            
            # Handle content lines
            elif in_section:
                current_section_content.append(line)
        
        return metadata, sections
    
    def _parse_section_info(self, block_type: str, label: Optional[str]) -> Dict:
        """
        Parse section information from block type and label
        
        Args:
            block_type: ChordPro block type (e.g., 'verse', 'chorus')
            label: Optional section label from comment
            
        Returns:
            Dictionary with name, type, and number
        """
        section_name = block_type.title()
        section_type = block_type
        section_number = None
        
        if label:
            section_name = label
            label_lower = label.lower()
            
            # Try to extract number from label
            match = re.match(r'([a-zA-Zéèêàâùû\s]+)\s*(\d+|[a-zA-Z])$', label_lower)
            
            type_part = label_lower
            if match:
                type_part = match.group(1).strip()
                section_number = match.group(2)
            
            # Find standardized type
            for key, value in self.config.label_to_type_map.items():
                if key in type_part:
                    section_type = value
                    break
        
        return {
            'name': section_name,
            'type': section_type,
            'number': section_number
        }
    
    def _create_section(self, section_info: Dict, content: List[str]) -> ChordProSection:
        """
        Create ChordProSection from parsed information
        
        Args:
            section_info: Dictionary with section metadata
            content: List of content lines
            
        Returns:
            ChordProSection instance
        """
        return ChordProSection(
            name=section_info['name'],
            type=section_info['type'],
            number=section_info.get('number'),
            content=content,
            raw_content='\n'.join(content)
        )
    
    def parse_chord_line(self, line: str) -> ParsedLine:
        """
        Parse a line with chords and return chord positions and clean text
        
        Args:
            line: Line to parse
            
        Returns:
            ParsedLine with chords and text
        """
        chords = []
        
        # Find all chord matches
        chord_matches = list(self.chord_pattern.finditer(line))
        
        # Calculate adjusted positions and build chord list
        for i, match in enumerate(chord_matches):
            chord = match.group(1)
            original_pos = match.start()
            
            # Calculate adjusted position by subtracting lengths of previous chord brackets
            adjusted_pos = original_pos
            for prev_match in chord_matches[:i]:
                prev_chord_text = f"[{prev_match.group(1)}]"
                adjusted_pos -= len(prev_chord_text)
            
            # Create chord position
            chord_id = hashlib.md5(f"{chord}{original_pos}".encode('utf-8')).hexdigest()[:5]
            chords.append(ChordPosition(
                id=chord_id,
                pos=max(0, adjusted_pos),
                key=chord
            ))
        
        # Remove chord brackets from text
        clean_text = self.chord_pattern.sub('', line)
        
        # Remove leading numbers like "1. "
        clean_text = re.sub(r'^\d+\.\s*', '', clean_text)
        
        return ParsedLine(text=clean_text, chords=chords)
    
    @staticmethod
    def deduplicate_sections(sections: List[ChordProSection]) -> Tuple[List[ChordProSection], List[int]]:
        """
        Deduplicate repeated sections and create a map of original to unique indices
        
        Args:
            sections: List of ChordProSection objects
            
        Returns:
            Tuple of (unique sections list, index map)
        """
        unique_sections = []
        section_map = {}  # Maps content hash to index in unique_sections
        index_map = []  # Maps original section index to unique section index
        
        for section in sections:
            content_hash = section.get_content_hash()
            
            if content_hash in section_map:
                # This is a duplicate
                unique_index = section_map[content_hash]
                index_map.append(unique_index)
            else:
                # This is a new unique section
                unique_index = len(unique_sections)
                section_map[content_hash] = unique_index
                index_map.append(unique_index)
                unique_sections.append(section)
        
        logger.debug(f"Deduplicated {len(sections)} sections to {len(unique_sections)} unique sections")
        
        return unique_sections, index_map
