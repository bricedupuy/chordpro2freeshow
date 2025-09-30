"""
Configuration management for ChordPro processor
"""

import json
from dataclasses import dataclass, field
from typing import Dict, Optional
from pathlib import Path

# Optional YAML support
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@dataclass
class ProcessorConfig:
    """Configuration for ChordPro processor"""
    
    # Online resource URLs
    jemaf_base_url: str = "https://jemaf.fr/ressources/chordPro/"
    csv_url: str = "https://raw.githubusercontent.com/bricedupuy/jemaf_chordpro_enhancer/refs/heads/main/custom-metadata.csv"
    
    # Output directories
    default_chordpro_output: str = "processedChordPro"
    default_freeshow_output: str = "processedFreeShow"
    
    # Network settings
    connection_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Processing settings
    fix_french_punctuation: bool = True
    deduplicate_sections: bool = True
    
    # FreeShow slide colors by section type
    section_colors: Dict[str, str] = field(default_factory=lambda: {
        'verse': '',
        'chorus': '#f525d2',
        'bridge': '#f52598',
        'pre_chorus': '#25d2f5',
        'tag': '#f5d225',
        'intro': '',
        'outro': ''
    })
    
    # FreeShow global groups mapping
    global_groups: Dict[str, str] = field(default_factory=lambda: {
        'verse': 'verse',
        'chorus': 'chorus',
        'bridge': 'bridge',
        'pre_chorus': 'pre_chorus',
        'tag': 'tag',
        'intro': 'intro',
        'outro': 'outro'
    })
    
    # Section type mappings (for parsing ChordPro labels)
    label_to_type_map: Dict[str, str] = field(default_factory=lambda: {
        'refrain': 'chorus',
        'chorus': 'chorus',
        'strophe': 'verse',
        'verse': 'verse',
        'pont': 'bridge',
        'bridge': 'bridge',
        'introduction': 'intro',
        'intro': 'intro',
        'fin': 'outro',
        'outro': 'outro',
    })
    
    # FreeShow slide styling
    slide_style: str = "top:120px;left:50px;height:840px;width:1820px;"
    font_size: int = 100
    
    @classmethod
    def from_file(cls, filepath: str) -> 'ProcessorConfig':
        """
        Load configuration from YAML or JSON file
        
        Args:
            filepath: Path to configuration file
            
        Returns:
            ProcessorConfig instance
            
        Raises:
            ValueError: If file format is unsupported
            FileNotFoundError: If file doesn't exist
        """
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                if not YAML_AVAILABLE:
                    raise ImportError(
                        "PyYAML is required for YAML config files. "
                        "Install it with: pip install pyyaml"
                    )
                data = yaml.safe_load(f)
            elif path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {path.suffix}")
        
        return cls(**data)
    
    def to_file(self, filepath: str):
        """
        Save configuration to YAML or JSON file
        
        Args:
            filepath: Path to save configuration
        """
        path = Path(filepath)
        
        # Convert to dictionary
        data = {
            'jemaf_base_url': self.jemaf_base_url,
            'csv_url': self.csv_url,
            'default_chordpro_output': self.default_chordpro_output,
            'default_freeshow_output': self.default_freeshow_output,
            'connection_timeout': self.connection_timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'fix_french_punctuation': self.fix_french_punctuation,
            'deduplicate_sections': self.deduplicate_sections,
            'section_colors': self.section_colors,
            'global_groups': self.global_groups,
            'label_to_type_map': self.label_to_type_map,
            'slide_style': self.slide_style,
            'font_size': self.font_size
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                if not YAML_AVAILABLE:
                    raise ImportError(
                        "PyYAML is required for YAML config files. "
                        "Install it with: pip install pyyaml"
                    )
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            elif path.suffix == '.json':
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported configuration file format: {path.suffix}")
    
    def validate(self) -> bool:
        """
        Validate configuration values
        
        Returns:
            True if valid, raises ValueError if invalid
        """
        if self.connection_timeout <= 0:
            raise ValueError("connection_timeout must be positive")
        
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        
        if self.retry_delay < 0:
            raise ValueError("retry_delay must be non-negative")
        
        if self.font_size <= 0:
            raise ValueError("font_size must be positive")
        
        return True
