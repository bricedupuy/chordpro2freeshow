"""
Setup script for ChordPro to FreeShow Processor
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
else:
    requirements = ["pyyaml>=6.0", "tqdm>=4.65.0"]

setup(
    name="chordpro-freeshow-processor",
    version="2.0.0",
    author="ChordPro Processor Team",
    author_email="your.email@example.com",
    description="Convert ChordPro files to FreeShow presentation format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/chordpro-processor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics :: Presentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "chordpro-processor=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="chordpro freeshow presentation music lyrics converter",
)
