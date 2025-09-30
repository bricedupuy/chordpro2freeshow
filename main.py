#!/usr/bin/env python3
"""
ChordPro to FreeShow Batch Processor - Refactored Version

Main entry point for the application.

Usage: 
  python main.py                                      # Interactive online mode
  python main.py --local <input_dir> [csv_file] [output_dir]
  python main.py --config config.yaml                 # Use custom config
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional

from config import ProcessorConfig
from models import ProcessedFile
from processor import ChordProProcessor
from network import OnlineResourceManager
from cli import interactive_song_selection, display_summary
from utils import setup_logging, temporary_directory

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="ChordPro to FreeShow Processor with Online Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                      # Interactive online mode
  python main.py --local /path/to/chordpro/files     # Local mode with default CSV
  python main.py --local /path/to/files metadata.csv /path/to/output
  python main.py --config config.yaml                # Use custom configuration
  python main.py --parallel 10                       # Process 10 files in parallel
        """
    )
    
    parser.add_argument('--local', action='store_true', 
                       help='Use local files instead of online resources')
    parser.add_argument('--config', type=str, 
                       help='Path to configuration file (YAML or JSON)')
    parser.add_argument('--parallel', type=int, default=1,
                       help='Number of parallel workers (default: 1, max: 10)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--log-file', type=str,
                       help='Write logs to file')
    
    parser.add_argument('input_dir', nargs='?', 
                       help='Input directory (local mode only)')
    parser.add_argument('csv_file', nargs='?', 
                       help='CSV metadata file (local mode only)')
    parser.add_argument('output_dir', nargs='?', 
                       help='Output directory (optional)')
    
    return parser.parse_args()


def process_single_file(processor: ChordProProcessor, filepath: str, 
                       chordpro_output_dir: Path, freeshow_output_dir: Path) -> ProcessedFile:
    """
    Process a single ChordPro file
    
    Args:
        processor: ChordProProcessor instance
        filepath: Path to input file
        chordpro_output_dir: Output directory for enhanced ChordPro files
        freeshow_output_dir: Output directory for FreeShow files
        
    Returns:
        ProcessedFile with paths to all generated files
        
    Raises:
        Exception: If processing fails
    """
    filename = Path(filepath).name
    logger.info(f"Processing: {filename}")
    
    # Enhance ChordPro file
    enhanced_path = processor.enhance_chordpro(filepath, str(chordpro_output_dir))
    logger.info(f"  Enhanced: {Path(enhanced_path).name}")
    
    # Generate FreeShow file
    show_path = processor.generate_freeshow_file(enhanced_path, str(freeshow_output_dir))
    logger.info(f"  Show file: {Path(show_path).name}")
    
    return ProcessedFile(
        original=filepath,
        enhanced=enhanced_path,
        show=show_path
    )


def process_files_batch(processor: ChordProProcessor, 
                       files: List[str],
                       chordpro_output_dir: Path,
                       freeshow_output_dir: Path,
                       max_workers: int = 1) -> List[ProcessedFile]:
    """
    Process multiple files with optional parallelization
    
    Args:
        processor: ChordProProcessor instance
        files: List of file paths to process
        chordpro_output_dir: Output directory for ChordPro files
        freeshow_output_dir: Output directory for FreeShow files
        max_workers: Number of parallel workers (1 = sequential)
        
    Returns:
        List of ProcessedFile objects
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    # Try to import tqdm, fall back to simple counter if not available
    try:
        from tqdm import tqdm
        TQDM_AVAILABLE = True
    except ImportError:
        TQDM_AVAILABLE = False
        logger.warning("tqdm not installed. Install it for progress bars: pip install tqdm")
    
    processed_files = []
    failed_files = []
    
    if max_workers > 1:
        logger.info(f"Processing {len(files)} files with {max_workers} workers...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    process_single_file, 
                    processor, 
                    file, 
                    chordpro_output_dir, 
                    freeshow_output_dir
                ): file 
                for file in files
            }
            
            if TQDM_AVAILABLE:
                with tqdm(total=len(files), desc="Processing files") as pbar:
                    for future in as_completed(futures):
                        filename = futures[future]
                        try:
                            result = future.result()
                            processed_files.append(result)
                        except Exception as e:
                            logger.error(f"Failed to process {filename}: {e}")
                            failed_files.append(filename)
                        finally:
                            pbar.update(1)
            else:
                # Simple progress without tqdm
                completed = 0
                for future in as_completed(futures):
                    filename = futures[future]
                    completed += 1
                    try:
                        result = future.result()
                        processed_files.append(result)
                        logger.info(f"[{completed}/{len(files)}] Completed: {Path(filename).name}")
                    except Exception as e:
                        logger.error(f"[{completed}/{len(files)}] Failed: {filename}: {e}")
                        failed_files.append(filename)
    else:
        logger.info(f"Processing {len(files)} files sequentially...")
        
        if TQDM_AVAILABLE:
            iterator = tqdm(files, desc="Processing files")
        else:
            iterator = files
        
        for i, filepath in enumerate(iterator, 1):
            try:
                result = process_single_file(
                    processor, 
                    filepath, 
                    chordpro_output_dir, 
                    freeshow_output_dir
                )
                processed_files.append(result)
                if not TQDM_AVAILABLE:
                    logger.info(f"[{i}/{len(files)}] Completed: {Path(filepath).name}")
            except Exception as e:
                logger.error(f"Failed to process {filepath}: {e}")
                failed_files.append(filepath)
    
    if failed_files:
        logger.warning(f"\nFailed to process {len(failed_files)} files:")
        for filename in failed_files:
            logger.warning(f"  - {filename}")
    
    return processed_files


def run_local_mode(args, config: ProcessorConfig):
    """Run processor in local mode"""
    if not args.input_dir:
        logger.error("Input directory is required for local mode")
        sys.exit(1)
    
    input_dir = Path(args.input_dir)
    
    # Validate input directory
    if not input_dir.is_dir():
        logger.error(f"Input directory '{input_dir}' does not exist")
        sys.exit(1)
    
    # Determine CSV file
    csv_file = None
    if args.csv_file:
        csv_file = Path(args.csv_file)
        if not csv_file.is_file():
            logger.error(f"CSV file '{csv_file}' does not exist")
            sys.exit(1)
    else:
        logger.info("No CSV file provided, attempting to download online metadata...")
        with temporary_directory() as temp_dir:
            csv_file = OnlineResourceManager.download_csv_metadata(temp_dir, config)
            if csv_file:
                logger.info("Using online CSV metadata")
            else:
                logger.warning("Could not download online CSV, proceeding without enhanced metadata")
                # Create minimal dummy CSV
                csv_file = temp_dir / "dummy.csv"
                csv_file.write_text("Fichier;Titre\n", encoding='utf-8')
    
    # Set up output directories
    chordpro_output = Path(args.output_dir) if args.output_dir else Path(config.default_chordpro_output)
    freeshow_output = Path(config.default_freeshow_output)
    
    chordpro_output.mkdir(parents=True, exist_ok=True)
    freeshow_output.mkdir(parents=True, exist_ok=True)
    
    # Initialize processor
    processor = ChordProProcessor(str(csv_file), config)
    
    # Find all ChordPro files
    chordpro_files = list(input_dir.glob("*.chordpro"))
    
    if not chordpro_files:
        logger.warning(f"No .chordpro files found in '{input_dir}'")
        sys.exit(0)
    
    logger.info(f"Found {len(chordpro_files)} ChordPro files")
    
    # Process files
    processed = process_files_batch(
        processor,
        [str(f) for f in chordpro_files],
        chordpro_output,
        freeshow_output,
        max_workers=min(args.parallel, 10)
    )
    
    # Display summary
    display_summary(processed, processor, chordpro_output, freeshow_output)


def run_online_mode(args, config: ProcessorConfig):
    """Run processor in online mode"""
    logger.info("ChordPro to FreeShow Processor - Online Mode")
    logger.info("=" * 50)
    logger.info("Fetching available songs from JEMAF repository...")
    
    with temporary_directory() as temp_dir:
        # Get available files
        available_files = OnlineResourceManager.get_available_files(config)
        if not available_files:
            logger.error("Could not fetch file list from JEMAF repository")
            sys.exit(1)
        
        logger.info(f"Found {len(available_files)} songs available online")
        
        # Download CSV metadata
        logger.info("Downloading song metadata...")
        csv_file = OnlineResourceManager.download_csv_metadata(temp_dir, config)
        
        if not csv_file:
            logger.warning("Could not download metadata CSV. Proceeding without enhanced metadata.")
            csv_file = temp_dir / "dummy.csv"
            csv_file.write_text("Fichier;Titre\n", encoding='utf-8')
        
        # Initialize processor
        processor = ChordProProcessor(str(csv_file), config)
        
        # Interactive song selection
        selected_files = interactive_song_selection(available_files, processor.metadata)
        
        if not selected_files:
            logger.info("No files selected. Exiting.")
            sys.exit(0)
        
        # Set up output directories
        chordpro_output = Path(args.output_dir) if args.output_dir else Path(config.default_chordpro_output)
        freeshow_output = Path(config.default_freeshow_output)
        
        chordpro_output.mkdir(parents=True, exist_ok=True)
        freeshow_output.mkdir(parents=True, exist_ok=True)
        
        # Download and process files
        logger.info(f"\nDownloading and processing {len(selected_files)} files...")
        
        downloaded_files = []
        for filename in selected_files:
            local_path = OnlineResourceManager.download_file(filename, temp_dir, config)
            if local_path:
                downloaded_files.append(str(local_path))
            else:
                logger.error(f"Could not download {filename}")
        
        if not downloaded_files:
            logger.error("No files were successfully downloaded")
            sys.exit(1)
        
        # Process downloaded files
        processed = process_files_batch(
            processor,
            downloaded_files,
            chordpro_output,
            freeshow_output,
            max_workers=min(args.parallel, 10)
        )
        
        # Display summary
        display_summary(processed, processor, chordpro_output, freeshow_output)


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level, args.log_file)
    
    # Load configuration
    config = ProcessorConfig.from_file(args.config) if args.config else ProcessorConfig()
    
    try:
        if args.local:
            run_local_mode(args, config)
        else:
            run_online_mode(args, config)
            
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
