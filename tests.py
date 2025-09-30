"""
Unit tests for ChordPro processor
Run with: pytest test_processor.py
"""

import pytest
import tempfile
from pathlib import Path

from config import ProcessorConfig
from models import SongMetadata, ChordProSection
from parsers import ChordProParser, MetadataLoader
from utils import (
    sanitize_filename, 
    normalize_chordpro_filename, 
    extract_number_from_filename,
    FrenchPunctuationHandler,
    extract_year_from_copyright
)


class TestUtils:
    """Test utility functions"""
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        assert sanitize_filename("jem001.chordpro") == "jem001.chordpro"
        assert sanitize_filename("../../etc/passwd") == "passwd"
        assert sanitize_filename("file with spaces.txt") == "file_with_spaces.txt"
        assert sanitize_filename("file@#$%^&*.txt") == "file______.txt"
    
    def test_normalize_chordpro_filename(self):
        """Test ChordPro filename normalization"""
        assert normalize_chordpro_filename("jem917_0.chordpro") == "jem917.chordpro"
        assert normalize_chordpro_filename("jem5.chordpro") == "jem005.chordpro"
        assert normalize_chordpro_filename("jemk10.chordpro") == "jemk010.chordpro"
    
    def test_extract_number_from_filename(self):
        """Test number extraction for sorting"""
        assert extract_number_from_filename("jem001.chordpro") == (0, 1)
        assert extract_number_from_filename("jem999.chordpro") == (0, 999)
        assert extract_number_from_filename("jemk001.chordpro") == (1, 1)
        assert extract_number_from_filename("other.txt") == (2, 0)
    
    def test_extract_year_from_copyright(self):
        """Test year extraction from copyright text"""
        assert extract_year_from_copyright("© 2020 Artist Name") == "2020"
        assert extract_year_from_copyright("Copyright 1995-2023") == "1995"
        assert extract_year_from_copyright("No year here") is None


class TestFrenchPunctuation:
    """Test French punctuation handling"""
    
    def test_fix_semicolon(self):
        """Test semicolon spacing"""
        handler = FrenchPunctuationHandler
        result = handler.fix_french_punctuation("Bonjour ; comment allez-vous")
        assert "\u00A0;" in result
    
    def test_fix_colon(self):
        """Test colon spacing"""
        handler = FrenchPunctuationHandler
        result = handler.fix_french_punctuation("Titre : Sous-titre")
        assert "\u00A0:" in result
    
    def test_fix_exclamation(self):
        """Test exclamation mark spacing"""
        handler = FrenchPunctuationHandler
        result = handler.fix_french_punctuation("Magnifique !")
        assert "\u00A0!" in result
    
    def test_fix_question_mark(self):
        """Test question mark spacing"""
        handler = FrenchPunctuationHandler
        result = handler.fix_french_punctuation("Comment vas-tu ?")
        assert "\u00A0?" in result
    
    def test_fix_guillemets(self):
        """Test French quotation marks"""
        handler = FrenchPunctuationHandler
        result = handler.fix_french_punctuation("« Texte »")
        assert "«\u00A0" in result
        assert "\u00A0»" in result
    
    def test_none_input(self):
        """Test handling of None input"""
        handler = FrenchPunctuationHandler
        assert handler.fix_french_punctuation(None) is None
        assert handler.fix_french_punctuation("") == ""


class TestConfig:
    """Test configuration management"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = ProcessorConfig()
        assert config.connection_timeout == 30
        assert config.max_retries == 3
        assert config.fix_french_punctuation is True
        assert config.deduplicate_sections is True
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = ProcessorConfig()
        assert config.validate() is True
        
        # Test invalid timeout
        config.connection_timeout = -1
        with pytest.raises(ValueError):
            config.validate()
    
    def test_config_from_dict(self):
        """Test creating config with custom values"""
        config = ProcessorConfig(
            connection_timeout=60,
            max_retries=5,
            font_size=120
        )
        assert config.connection_timeout == 60
        assert config.max_retries == 5
        assert config.font_size == 120


class TestChordProParser:
    """Test ChordPro parsing"""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        config = ProcessorConfig()
        return ChordProParser(config)
    
    @pytest.fixture
    def sample_chordpro(self):
        """Create sample ChordPro content"""
        return """
{title: Test Song}
{artist: Test Artist}
{key: C}

{start_of_verse}
[C]This is a test [G]line
With some [Am]chords [F]here
{end_of_verse}

{start_of_chorus}
{c: Refrain}
[C]Chorus [G]lyrics
{end_of_chorus}
"""
    
    def test_parse_chord_line(self, parser):
        """Test chord line parsing"""
        line = "[C]Hello [G]world [Am]test"
        parsed = parser.parse_chord_line(line)
        
        assert parsed.text == "Hello world test"
        assert len(parsed.chords) == 3
        assert parsed.chords[0].key == "C"
        assert parsed.chords[1].key == "G"
        assert parsed.chords[2].key == "Am"
    
    def test_parse_file(self, parser, sample_chordpro):
        """Test full file parsing"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.chordpro', delete=False) as f:
            f.write(sample_chordpro)
            temp_path = f.name
        
        try:
            metadata, sections = parser.parse_file(temp_path)
            
            # Check metadata
            assert metadata['title'] == 'Test Song'
            assert metadata['artist'] == 'Test Artist'
            assert metadata['key'] == 'C'
            
            # Check sections
            assert len(sections) == 2
            assert sections[0].type == 'verse'
            assert sections[1].type == 'chorus'
            
        finally:
            Path(temp_path).unlink()
    
    def test_deduplicate_sections(self, parser):
        """Test section deduplication"""
        section1 = ChordProSection(
            name="Verse 1",
            type="verse",
            number="1",
            content=["Line 1", "Line 2"],
            raw_content="Line 1\nLine 2"
        )
        
        section2 = ChordProSection(
            name="Verse 2",
            type="verse",
            number="2",
            content=["Line 1", "Line 2"],  # Same content
            raw_content="Line 1\nLine 2"
        )
        
        section3 = ChordProSection(
            name="Verse 3",
            type="verse",
            number="3",
            content=["Different", "Content"],
            raw_content="Different\nContent"
        )
        
        unique, index_map = parser.deduplicate_sections([section1, section2, section3])
        
        assert len(unique) == 2  # Only 2 unique sections
        assert index_map == [0, 0, 1]  # Section 2 maps to section 1


class TestMetadataLoader:
    """Test CSV metadata loading"""
    
    @pytest.fixture
    def sample_csv(self):
        """Create sample CSV content"""
        return """Fichier;Titre;Auteur;Compositeur;Tonalité;Copyright
jem001;Test Song;Test Author;Test Composer;C;© 2020 Test
jem002;Another Song;Another Author;Another Composer;G;© 2021 Test"""
    
    def test_load_from_csv(self, sample_csv):
        """Test loading metadata from CSV"""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(sample_csv)
            temp_path = f.name
        
        try:
            metadata = MetadataLoader.load_from_csv(temp_path)
            
            assert 'jem001' in metadata
            assert metadata['jem001'].title == 'Test Song'
            assert metadata['jem001'].author == 'Test Author'
            assert metadata['jem001'].key == 'C'
            
            assert 'jem002' in metadata
            assert metadata['jem002'].title == 'Another Song'
            
        finally:
            Path(temp_path).unlink()


class TestModels:
    """Test data models"""
    
    def test_song_metadata_strips_whitespace(self):
        """Test that SongMetadata strips whitespace"""
        metadata = SongMetadata(
            number=" jem001 ",
            title=" Test Song ",
            title2="",
            original_title="",
            composer=" Composer ",
            author=" Author ",
            key=" C ",
            format="",
            copyright="",
            reference="",
            theme="",
            tune_of="",
            volume="",
            supplement="",
            f1="",
            link=""
        )
        
        assert metadata.number == "jem001"
        assert metadata.title == "Test Song"
        assert metadata.composer == "Composer"
        assert metadata.key == "C"
    
    def test_section_content_hash(self):
        """Test section content hashing"""
        section1 = ChordProSection(
            name="Test",
            type="verse",
            number="1",
            content=["Line 1", "{c: Comment}", "Line 2"],
            raw_content="Line 1\n{c: Comment}\nLine 2"
        )
        
        section2 = ChordProSection(
            name="Test",
            type="verse",
            number="2",
            content=["Line 1", "{c: Different comment}", "Line 2"],
            raw_content="Line 1\n{c: Different comment}\nLine 2"
        )
        
        # Hashes should be equal (comments ignored)
        assert section1.get_content_hash() == section2.get_content_hash()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
