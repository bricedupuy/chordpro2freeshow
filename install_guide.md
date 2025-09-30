# Installation Guide

## Quick Install

### Option 1: Automatic Installation (Recommended)

**Windows:**
```batch
install.bat
```

**Linux/Mac:**
```bash
python install.py
```

This will:
- Check Python version
- Check required files
- Install optional dependencies
- Create example configuration

### Option 2: Manual Installation

Install dependencies manually:

```bash
# Install optional dependencies (recommended)
pip install pyyaml tqdm

# Or install from requirements file
pip install -r requirements.txt
```

### Option 3: Minimal Installation (No Dependencies)

The processor can run without any external dependencies, but with reduced functionality:
- ❌ No YAML config support (JSON only)
- ❌ No progress bars (simple text output)
- ✅ All core processing features work

Just run directly:
```bash
python main.py
```

## Requirements

### System Requirements
- **Python**: 3.8 or higher
- **OS**: Windows, Linux, or macOS
- **Disk Space**: ~50MB for dependencies
- **Internet**: Required for online mode

### Python Dependencies

| Package | Required? | Purpose | Without It |
|---------|-----------|---------|------------|
| `pyyaml` | Optional | YAML config files | Use JSON configs instead |
| `tqdm` | Optional | Progress bars | See text progress |

## Installation Steps

### 1. Install Python

If you don't have Python installed:

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- Check "Add Python to PATH" during installation

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**macOS:**
```bash
brew install python3
```

### 2. Download the Processor

```bash
git clone <repository-url>
cd chordpro-processor
```

Or download and extract the ZIP file.

### 3. Install Dependencies

Choose one method:

**Method A: Automatic (Recommended)**
```bash
python install.py
```

**Method B: Using pip**
```bash
pip install pyyaml tqdm
```

**Method C: From requirements.txt**
```bash
pip install -r requirements.txt
```

**Method D: Skip (minimal install)**
- No installation needed, but reduced functionality

### 4. Verify Installation

```bash
python main.py --help
```

You should see the help message without errors.

## Troubleshooting

### "No module named 'yaml'"

**Solution 1: Install PyYAML**
```bash
pip install pyyaml
```

**Solution 2: Use JSON config instead**
- Create `config.json` instead of `config.yaml`
- The processor will work fine with JSON

### "No module named 'tqdm'"

**Solution 1: Install tqdm**
```bash
pip install tqdm
```

**Solution 2: Continue without it**
- The processor will work without progress bars
- You'll see simple text progress instead

### "Python is not recognized"

**Problem:** Python is not in your PATH

**Solution:**
- **Windows:** Reinstall Python and check "Add to PATH"
- **Linux/Mac:** Use `python3` instead of `python`

### Permission Errors

**Linux/Mac:**
```bash
# Use --user flag
pip install --user pyyaml tqdm

# Or use sudo (not recommended)
sudo pip install pyyaml tqdm
```

**Windows:**
- Run Command Prompt as Administrator
- Or use `--user` flag: `pip install --user pyyaml tqdm`

### Proxy Issues

If behind a corporate proxy:

```bash
pip install --proxy=http://proxy.server:port pyyaml tqdm
```

### Old pip Version

Update pip first:

```bash
python -m pip install --upgrade pip
```

Then install dependencies:

```bash
pip install pyyaml tqdm
```

## Virtual Environment (Optional but Recommended)

To avoid conflicts with other Python projects:

### Create Virtual Environment

**Windows:**
```batch
python -m venv venv
venv\Scripts\activate
pip install pyyaml tqdm
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install pyyaml tqdm
```

### Use with Virtual Environment

**Always activate first:**

**Windows:**
```batch
venv\Scripts\activate
python main.py
```

**Linux/Mac:**
```bash
source venv/bin/activate
python main.py
```

## Verification Checklist

After installation, verify:

- [ ] Python 3.8+ installed: `python --version`
- [ ] Dependencies installed: `pip list | grep -E "(pyyaml|tqdm)"`
- [ ] Processor runs: `python main.py --help`
- [ ] All module files present in directory

## Post-Installation

### Optional Configuration

Create a custom config file:

```bash
# Copy example config
cp config.example.yaml config.yaml

# Edit as needed
nano config.yaml  # or use your preferred editor
```

### Test Run

Try processing a file:

```bash
# Online mode (interactive)
python main.py

# Local mode (if you have files)
python main.py --local /path/to/files
```

## Updating

To update to the latest version:

```bash
# Pull latest code
git pull

# Update dependencies
pip install --upgrade pyyaml tqdm

# Verify
python main.py --help
```

## Uninstalling

To remove the processor:

```bash
# Remove dependencies (optional)
pip uninstall pyyaml tqdm

# Delete directory
cd ..
rm -rf chordpro-processor
```

## Getting Help

If you encounter issues:

1. Check this guide
2. Run with `--verbose` flag: `python main.py --verbose`
3. Check logs for errors
4. Open an issue on GitHub
5. Include error messages and Python version

## Minimal Working Example

To test if everything works:

```bash
# This should work even without dependencies
python -c "from config import ProcessorConfig; print('OK')"
```

If you see "OK", the basic installation is working.

## Platform-Specific Notes

### Windows
- Use backslashes in paths: `C:\Users\...`
- Or use forward slashes: `C:/Users/...`
- Run batch file: `install.bat`

### Linux
- May need `python3` instead of `python`
- May need `pip3` instead of `pip`
- Run script: `python3 install.py`

### macOS
- Use `python3` and `pip3`
- May need to accept Xcode tools
- Run script: `python3 install.py`

## Next Steps

After successful installation:

1. Read [README.md](README.md) for usage instructions
2. See [QUICKREF.md](QUICKREF.md) for quick commands
3. Check [MIGRATION.md](MIGRATION.md) if upgrading from old version
4. Run your first processing job!

---

**Need help?** Open an issue on GitHub with:
- Your OS and Python version
- Complete error message
- Output of `pip list`
