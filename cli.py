"""
Command-line interface utilities
"""

import re
import logging
from pathlib import Path
from typing import List, Dict

from models import SongMetadata, ProcessedFile
from processor import ChordProProcessor
from utils import normalize_chordpro_filename

logger = logging.getLogger(__name__)


def interactive_song_selection(available_files: List[str], 
                               metadata: Dict[str, SongMetadata]) -> List[str]:
    """
    Interactive selection of songs to process
    
    Args:
        available_files: List of available filenames
        metadata: Dictionary of song metadata
        
    Returns:
        List of selected filenames
    """
    print("\nAvailable songs:")
    print("=" * 80)
    
    # Display files with metadata when available
    for i, filename in enumerate(available_files, 1):
        base_name = normalize_chordpro_filename(filename)
        lookup_key = Path(base_name).stem.lower()
        
        display_line = f"{i:3d}. {base_name}"
        
        if lookup_key in metadata:
            song_meta = metadata[lookup_key]
            if song_meta.title:
                display_line += f" - {song_meta.title}"
            if song_meta.author:
                display_line += f" ({song_meta.author})"
        
        print(display_line)
        
        # Add spacing every 10 items for readability
        if i % 10 == 0:
            print()
    
    print("\nOptions:")
    print("  Enter specific numbers (e.g., 1,5,10-15): Process selected songs")
    print("  Enter 'all': Process all songs")
    print("  Enter 'search <term>': Search for songs containing the term")
    print("  Enter 'quit' or 'q': Exit")
    
    while True:
        choice = input("\nYour choice: ").strip().lower()
        
        if choice in ['quit', 'q']:
            return []
        
        if choice == 'all':
            return available_files
        
        if choice.startswith('search '):
            selected = _search_songs(choice[7:].strip(), available_files, metadata)
            if selected:
                return selected
            continue
        
        # Parse number ranges and individual numbers
        try:
            selected_files = _parse_number_selection(choice, available_files)
            if selected_files:
                return selected_files
        except ValueError as e:
            print(f"Invalid selection: {e}. Please try again.")
            continue


def _search_songs(search_term: str, 
                 available_files: List[str],
                 metadata: Dict[str, SongMetadata]) -> List[str]:
    """
    Search for songs matching a term
    
    Args:
        search_term: Term to search for
        available_files: List of available files
        metadata: Song metadata dictionary
        
    Returns:
        List of selected files or empty list if cancelled
    """
    search_term_lower = search_term.lower()
    matching_files = []
    
    print(f"\nSearching for '{search_term}':")
    
    for filename in available_files:
        base_name = normalize_chordpro_filename(filename)
        lookup_key = Path(base_name).stem.lower()
        
        # Search in filename
        match_found = search_term_lower in base_name.lower()
        
        # Search in metadata
        if lookup_key in metadata:
            song_meta = metadata[lookup_key]
            match_found = (match_found or 
                          search_term_lower in song_meta.title.lower() or
                          search_term_lower in song_meta.author.lower() or
                          search_term_lower in song_meta.composer.lower() or
                          search_term_lower in song_meta.theme.lower())
        
        if match_found:
            matching_files.append(filename)
            print(f"  {base_name}", end="")
            if lookup_key in metadata and metadata[lookup_key].title:
                print(f" - {metadata[lookup_key].title}")
            else:
                print()
    
    if not matching_files:
        print("  No matches found.")
        return []
    
    print(f"\nFound {len(matching_files)} matching songs.")
    confirm = input(f"Process these songs? (y/n): ").strip().lower()
    
    if confirm == 'y':
        return matching_files
    
    return []


def _parse_number_selection(choice: str, available_files: List[str]) -> List[str]:
    """
    Parse number selection from user input
    
    Args:
        choice: User input string
        available_files: List of available files
        
    Returns:
        List of selected files
        
    Raises:
        ValueError: If selection format is invalid
    """
    selected_indices = set()
    
    for part in choice.split(','):
        part = part.strip()
        
        if '-' in part:
            # Range like "10-15"
            try:
                start, end = part.split('-')
                start_idx = int(start) - 1  # Convert to 0-based
                end_idx = int(end)  # Inclusive end
                
                if start_idx < 0 or end_idx > len(available_files):
                    raise ValueError(f"Range {part} is out of bounds")
                
                selected_indices.update(range(start_idx, end_idx))
            except ValueError as e:
                raise ValueError(f"Invalid range format: {part}")
        else:
            # Individual number
            try:
                idx = int(part) - 1  # Convert to 0-based
                if idx < 0 or idx >= len(available_files):
                    raise ValueError(f"Number {part} is out of bounds")
                selected_indices.add(idx)
            except ValueError:
                raise ValueError(f"Invalid number: {part}")
    
    if not selected_indices:
        print("No valid selections made.")
        return []
    
    selected_files = [available_files[i] for i in sorted(selected_indices)]
    return selected_files


def display_summary(processed_files: List[ProcessedFile],
                   processor: ChordProProcessor,
                   chordpro_output_dir: Path,
                   freeshow_output_dir: Path):
    """
    Display summary of processed files
    
    Args:
        processed_files: List of ProcessedFile objects
        processor: ChordProProcessor instance
        chordpro_output_dir: ChordPro output directory
        freeshow_output_dir: FreeShow output directory
    """
    print(f"\n{'=' * 80}")
    print(f"Processing Complete!")
    print(f"{'=' * 80}")
    print(f"\nProcessed {len(processed_files)} files successfully")
    print(f"Enhanced ChordPro files: {chordpro_output_dir}")
    print(f"FreeShow files: {freeshow_output_dir}")
    
    if processed_files:
        print(f"\nProcessed songs:")
        print("-" * 80)
        
        for file_info in processed_files:
            title = file_info.get_title()
            filename = Path(file_info.enhanced).stem.replace('-enhanced', '')
            
            if title:
                print(f"  ✓ {filename} - {title}")
            else:
                print(f"  ✓ {filename}")
        
        print(f"\n{'=' * 80}")


def print_banner():
    """Print application banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          ChordPro to FreeShow Batch Processor                ║
║                                                               ║
║          Enhanced with metadata and French punctuation       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)