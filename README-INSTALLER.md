# Building Windows Installer for Inity

This guide explains how to create a professional Windows installer (.exe) for Inity.

## Prerequisites

1. **Windows OS** (Windows 10/11 recommended)
2. **Python 3.8+** installed and in PATH
3. **NSIS (Nullsoft Scriptable Install System)**
   - Download from: https://nsis.sourceforge.io/
   - Install and make sure `makensis.exe` is in your PATH

## Quick Build

```cmd
# Run the automated builder
build-installer.bat
```

Or manually:

```cmd
# Build the installer
python build-installer.py
```

## What the Installer Does

### 🔧 Installation Features:
- **Python Detection**: Automatically checks for Python 3.8+
- **Isolated Environment**: Creates dedicated virtual environment
- **Global Installation**: Installs Inity system-wide
- **PATH Integration**: Adds Inity to system PATH
- **Shortcuts**: Creates desktop and start menu shortcuts
- **Uninstaller**: Provides clean uninstall option

### 📦 Components:
- **Inity Core** (Required): Main application files
- **Add to PATH** (Optional): Global command-line access
- **Desktop Shortcut** (Optional): Desktop icon
- **Start Menu Shortcuts** (Optional): Start menu entries

## Installation Process for Users

1. **Download** the `Inity-X.X.X-Windows-Installer.exe`
2. **Run as Administrator** (right-click → "Run as administrator")
3. **Follow the wizard**:
   - Accept license
   - Choose components
   - Select installation directory
   - Complete installation
4. **Usage**: Open Command Prompt and type `inity --help`

## File Structure After Installation

```
C:\Program Files\Inity\
├── venv\                 # Python virtual environment
├── inity.exe            # Main executable wrapper
├── README.md            # Documentation
├── LICENSE              # License file
└── uninstall.exe        # Uninstaller
```

## Advanced Options

### Custom NSIS Build

You can modify `windows-installer.nsi` to customize:
- Installation directory
- Component options
- Registry entries
- File associations
- Custom actions

### Silent Installation

For deployment scenarios:
```cmd
Inity-X.X.X-Windows-Installer.exe /S
```

### Installation Logs

Enable logging:
```cmd
Inity-X.X.X-Windows-Installer.exe /S /L=install.log
```

## Troubleshooting

### Build Issues

**NSIS not found:**
```cmd
# Install NSIS and add to PATH
# Or specify full path in build-installer.py
```

**Python not found:**
```cmd
# Install Python from python.org
# Make sure "Add to PATH" is checked
```

### Installation Issues

**Python not detected:**
- Install Python 3.8+ from python.org
- Ensure "Add Python to PATH" is selected

**Permission denied:**
- Run installer as Administrator
- Check antivirus software

**PATH not updated:**
- Restart Command Prompt
- Or manually add installation directory to PATH

## Distribution

### For End Users:
1. Build the installer: `build-installer.bat`
2. Distribute the generated `.exe` file
3. Users run the installer and follow the wizard

### For Developers:
1. The installer includes source code protection
2. Creates isolated Python environment
3. Handles dependencies automatically
4. Provides clean uninstall

---

*Built with ❤️ by Aathish at Strucureo*
