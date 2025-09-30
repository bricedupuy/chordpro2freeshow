#!/usr/bin/env python3
"""
Installation and dependency check script for ChordPro Processor

This script checks for required dependencies and offers to install them.
Run this before using the main processor.
"""

import sys
import subprocess
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print installation header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}")
    print("  ChordPro to FreeShow Processor - Installation")
    print(f"{'='*70}{Colors.END}\n")

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...", end=" ")
    
    if sys.version_info < (3, 8):
        print(f"{Colors.RED}✗ FAIL{Colors.END}")
        print(f"{Colors.RED}Python 3.8 or higher is required.{Colors.END}")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"{Colors.GREEN}✓ OK{Colors.END} (Python {sys.version_info.major}.{sys.version_info.minor})")
    return True

def check_module(module_name, package_name=None):
    """
    Check if a Python module is installed
    
    Args:
        module_name: Name of module to import
        package_name: Name of package to install (if different from module)
    
    Returns:
        True if module is available, False otherwise
    """
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """
    Install a package using pip
    
    Args:
        package_name: Package to install
        
    Returns:
        True if successful, False otherwise
    """
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """Check all dependencies and offer to install missing ones"""
    
    # Required dependencies (core functionality)
    required_deps = []
    
    # Optional dependencies (enhanced features)
    optional_deps = [
        ("yaml", "pyyaml", "YAML configuration support"),
        ("tqdm", "tqdm", "Progress bars")
    ]
    
    print(f"\n{Colors.BOLD}Checking dependencies...{Colors.END}\n")
    
    # Check required dependencies
    all_required_ok = True
    for module, package, description in required_deps:
        print(f"  {description:.<50}", end=" ")
        if check_module(module, package):
            print(f"{Colors.GREEN}✓ Installed{Colors.END}")
        else:
            print(f"{Colors.RED}✗ Missing{Colors.END}")
            all_required_ok = False
    
    # Check optional dependencies
    missing_optional = []
    for module, package, description in optional_deps:
        print(f"  {description:.<50}", end=" ")
        if check_module(module, package):
            print(f"{Colors.GREEN}✓ Installed{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠ Missing (optional){Colors.END}")
            missing_optional.append((module, package, description))
    
    # Offer to install missing optional dependencies
    if missing_optional:
        print(f"\n{Colors.YELLOW}Some optional dependencies are missing.{Colors.END}")
        print("The program will work without them, but with reduced functionality.")
        
        response = input("\nWould you like to install them? (y/n): ").strip().lower()
        
        if response in ['y', 'yes']:
            print(f"\n{Colors.BOLD}Installing optional dependencies...{Colors.END}\n")
            
            for module, package, description in missing_optional:
                print(f"  Installing {package}...", end=" ")
                if install_package(package):
                    print(f"{Colors.GREEN}✓ Success{Colors.END}")
                else:
                    print(f"{Colors.RED}✗ Failed{Colors.END}")
                    print(f"    {Colors.YELLOW}Try manually: pip install {package}{Colors.END}")
    
    return all_required_ok

def check_files():
    """Check if required files exist"""
    print(f"\n{Colors.BOLD}Checking required files...{Colors.END}\n")
    
    required_files = [
        "main.py",
        "config.py",
        "models.py",
        "parsers.py",
        "processor.py",
        "network.py",
        "cli.py",
        "utils.py"
    ]
    
    all_ok = True
    for filename in required_files:
        print(f"  {filename:.<50}", end=" ")
        if Path(filename).exists():
            print(f"{Colors.GREEN}✓ Found{Colors.END}")
        else:
            print(f"{Colors.RED}✗ Missing{Colors.END}")
            all_ok = False
    
    return all_ok

def create_example_config():
    """Create example configuration file if it doesn't exist"""
    config_file = Path("config.example.yaml")
    
    if config_file.exists():
        return
    
    example_config = """# ChordPro Processor Configuration
# Copy to config.yaml and customize

# Network settings
connection_timeout: 30
max_retries: 3

# Output directories
default_chordpro_output: "processedChordPro"
default_freeshow_output: "processedFreeShow"

# Processing
fix_french_punctuation: true
deduplicate_sections: true
font_size: 100
"""
    
    try:
        config_file.write_text(example_config, encoding='utf-8')
        print(f"\n{Colors.GREEN}✓{Colors.END} Created example config: {config_file}")
    except Exception as e:
        print(f"\n{Colors.YELLOW}⚠{Colors.END} Could not create example config: {e}")

def print_summary():
    """Print installation summary and next steps"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}")
    print("  Installation Complete!")
    print(f"{'='*70}{Colors.END}\n")
    
    print(f"{Colors.BOLD}Next steps:{Colors.END}\n")
    print("  1. Run the processor:")
    print(f"     {Colors.GREEN}python main.py{Colors.END}")
    print()
    print("  2. For local files:")
    print(f"     {Colors.GREEN}python main.py --local /path/to/files{Colors.END}")
    print()
    print("  3. For help:")
    print(f"     {Colors.GREEN}python main.py --help{Colors.END}")
    print()
    print(f"{Colors.BOLD}Optional:{Colors.END}")
    print("  • Create custom config: Copy config.example.yaml to config.yaml")
    print("  • View documentation: README.md")
    print("  • View quick reference: QUICKREF.md")
    print()

def main():
    """Main installation function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check required files
    if not check_files():
        print(f"\n{Colors.RED}Error: Some required files are missing.{Colors.END}")
        print("Please ensure you have all the processor files.")
        sys.exit(1)
    
    # Check and install dependencies
    if not check_and_install_dependencies():
        print(f"\n{Colors.RED}Error: Required dependencies are missing.{Colors.END}")
        sys.exit(1)
    
    # Create example config
    create_example_config()
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Installation cancelled by user.{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n{Colors.RED}Unexpected error: {e}{Colors.END}")
        sys.exit(1)
