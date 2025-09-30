"""
Network utilities for downloading ChordPro files and metadata
"""

import re
import time
import logging
import urllib.request
from pathlib import Path
from typing import List, Optional
from urllib.error import URLError, HTTPError

from config import ProcessorConfig
from utils import sanitize_filename, normalize_chordpro_filename, extract_number_from_filename

logger = logging.getLogger(__name__)


class OnlineResourceManager:
    """Manages online resource access for JEMAF ChordPro files"""
    
    @classmethod
    def get_available_files(cls, config: ProcessorConfig) -> List[str]:
        """
        Get list of available ChordPro files from JEMAF website
        
        Args:
            config: ProcessorConfig instance
            
        Returns:
            List of filenames available for download
        """
        for attempt in range(config.max_retries):
            try:
                logger.debug(f"Fetching file list from {config.jemaf_base_url} (attempt {attempt + 1})")
                
                request = urllib.request.Request(
                    config.jemaf_base_url,
                    headers={'User-Agent': 'ChordProProcessor/1.0'}
                )
                
                with urllib.request.urlopen(request, timeout=config.connection_timeout) as response:
                    html_content = response.read().decode('utf-8', errors='replace')
                
                # Find all links to .chordpro files using regex
                files = re.findall(r'href="([^"]+\.chordpro)"', html_content)
                
                if not files:
                    logger.warning("No .chordpro files found in HTML")
                    return []
                
                # Sort files naturally (handles both jem and jemk files)
                files.sort(key=extract_number_from_filename)
                
                logger.info(f"Found {len(files)} ChordPro files")
                return files
                
            except HTTPError as e:
                logger.error(f"HTTP error fetching file list: {e.code} - {e.reason}")
                if attempt < config.max_retries - 1:
                    time.sleep(config.retry_delay)
                    continue
                return []
                
            except URLError as e:
                logger.error(f"Network error fetching file list: {e.reason}")
                if attempt < config.max_retries - 1:
                    time.sleep(config.retry_delay)
                    continue
                return []
                
            except Exception as e:
                logger.exception(f"Unexpected error fetching file list: {e}")
                return []
        
        return []
    
    @classmethod
    def download_file(cls, filename: str, temp_dir: Path, config: ProcessorConfig) -> Optional[Path]:
        """
        Download a single ChordPro file to temporary directory
        
        Args:
            filename: Name of file to download
            temp_dir: Directory to save file
            config: ProcessorConfig instance
            
        Returns:
            Path to downloaded file or None if failed
        """
        url = config.jemaf_base_url + filename
        
        # Normalize and sanitize filename
        normalized_filename = normalize_chordpro_filename(filename)
        normalized_filename = sanitize_filename(normalized_filename)
        local_path = temp_dir / normalized_filename
        
        for attempt in range(config.max_retries):
            try:
                logger.debug(f"Downloading {filename} from {url} (attempt {attempt + 1})")
                
                request = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'ChordProProcessor/1.0'}
                )
                
                with urllib.request.urlopen(request, timeout=config.connection_timeout) as response:
                    content = response.read().decode('utf-8', errors='replace')
                
                local_path.write_text(content, encoding='utf-8')
                logger.debug(f"Downloaded to {local_path}")
                
                return local_path
                
            except HTTPError as e:
                logger.error(f"HTTP error downloading {filename}: {e.code} - {e.reason}")
                if attempt < config.max_retries - 1:
                    time.sleep(config.retry_delay)
                    continue
                return None
                
            except URLError as e:
                logger.error(f"Network error downloading {filename}: {e.reason}")
                if attempt < config.max_retries - 1:
                    time.sleep(config.retry_delay)
                    continue
                return None
                
            except Exception as e:
                logger.exception(f"Unexpected error downloading {filename}: {e}")
                return None
        
        return None
    
    @classmethod
    def download_csv_metadata(cls, temp_dir: Path, config: ProcessorConfig) -> Optional[Path]:
        """
        Download CSV metadata file to temporary directory
        
        Args:
            temp_dir: Directory to save CSV
            config: ProcessorConfig instance
            
        Returns:
            Path to downloaded CSV or None if failed
        """
        local_path = temp_dir / "custom-metadata.csv"
        
        for attempt in range(config.max_retries):
            try:
                logger.debug(f"Downloading CSV metadata from {config.csv_url} (attempt {attempt + 1})")
                
                request = urllib.request.Request(
                    config.csv_url,
                    headers={'User-Agent': 'ChordProProcessor/1.0'}
                )
                
                with urllib.request.urlopen(request, timeout=config.connection_timeout) as response:
                    content = response.read().decode('utf-8', errors='replace')
                
                local_path.write_text(content, encoding='utf-8')
                logger.info(f"Downloaded CSV metadata to {local_path}")
                
                return local_path
                
            except HTTPError as e:
                logger.error(f"HTTP error downloading CSV metadata: {e.code} - {e.reason}")
                if attempt < config.max_retries - 1:
                    time.sleep(config.retry_delay)
                    continue
                return None
                
            except URLError as e:
                logger.error(f"Network error downloading CSV metadata: {e.reason}")
                if attempt < config.max_retries - 1:
                    time.sleep(config.retry_delay)
                    continue
                return None
                
            except Exception as e:
                logger.exception(f"Unexpected error downloading CSV metadata: {e}")
                return None
        
        return None
