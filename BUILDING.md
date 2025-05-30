# Building Inity

**Intelligent Python project environment setup tool**  
*Developed by Aathish at Strucureo*

This guide explains how to build Inity executables for Windows, Linux, and macOS.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (optional, for cloning)

## Quick Build

### All Platforms

```bash
# Clone repository
git clone https://github.com/strucureo/inity.git
cd inity

# Build for your current platform
python build.py
```

### Platform-Specific Scripts

**Windows:**
```cmd
build.bat
```

**Linux/macOS:**
```bash
chmod +x build.sh
./build.sh
```

**Using Make:**
```bash
make build
```

## Manual Build Process

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Build Executable

```bash
# Using PyInstaller directly
pyinstaller inity.spec

# Or using build script
python build.py
```

### 3. Test Executable

```bash
# Test the built executable
./dist/inity --help           # Linux/macOS
.\dist\inity.exe --help       # Windows
```

## Output Files

After building, you'll find:

```
dist/
├── inity(.exe)                 # Main executable
├── inity-windows.zip          # Windows distribution
├── inity-macos.zip            # macOS distribution
└── inity-linux.zip            # Linux distribution
```

## Distribution Packages

Each platform package includes:

- **inity executable** - Main program
- **install script** - Automated installation
- **README.txt** - Usage instructions

### Windows Distribution
- `inity.exe` - Windows executable
- `README.txt` - Installation guide

### macOS Distribution
- `inity` - macOS executable
- `install.sh` - Installation script
- `README.txt` - Usage guide

### Linux Distribution
- `inity` - Linux executable
- `install.sh` - Installation script  
- `README.txt` - Usage instructions

## Installation

### Windows
1. Extract `inity-windows.zip`
2. Copy `inity.exe` to a folder in your PATH
3. Or run from any location: `.\inity.exe --help`

### macOS
1. Extract `inity-macos.zip`
2. Run: `chmod +x install.sh && ./install.sh`
3. Or manually: `sudo cp inity /usr/local/bin/`

### Linux
1. Extract `inity-linux.zip`
2. Run: `chmod +x install.sh && ./install.sh`
3. Or manually copy to `/usr/local/bin/` or `~/.local/bin/`

## Usage

After installation, use Inity from any directory:

```bash
# Create new project
inity create my-awesome-project

# Package management
inity package search fastapi
inity package install requests

# Get help
inity --help
```

## Troubleshooting

### Build Issues

**ImportError during build:**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt
```

**PyInstaller not found:**
```bash
pip install pyinstaller>=6.0.0
```

### Runtime Issues

**Command not found:**
- Ensure the executable is in your PATH
- On Linux/macOS, make sure it's executable: `chmod +x inity`

**Permission denied:**
- On Linux/macOS: `chmod +x inity`
- On Windows: Run as Administrator if needed

## Development Build

For development with auto-reload:

```bash
# Install in development mode
pip install -e .

# Run directly
python -m smartenv.main --help
```

## Contributing

To contribute to Inity:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the build process
5. Submit a pull request

---

*Built with ❤️ by Aathish at Strucureo*
