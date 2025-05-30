# Installing Inity

**Intelligent Python project environment setup tool**  
*Developed by Aathish at Strucureo*

## 🚀 Quick Install (Recommended)

### One-Command Installation

**Linux/macOS:**
```bash
curl -sSL https://raw.githubusercontent.com/theaathish/Inity/main/install.sh | bash
```

**Windows (PowerShell as Administrator):**
```powershell
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/theaathish/Inity/main/install.ps1'))
```

## 📋 Prerequisites

- **Python 3.8+** installed and in PATH
- **pip** package manager
- **Internet connection** for package installation

### Installing Python (if needed)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**macOS:**
```bash
brew install python
```

**Windows:**
- Download from [python.org](https://python.org)
- Check "Add Python to PATH" during installation

## 🔧 Manual Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/theaathish/Inity.git
cd Inity
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Install Inity
```bash
pip install -e .
```

### Step 4: Verify Installation
```bash
inity --version
```

## 🐳 Docker Installation

```bash
# Build Docker image
docker build -t inity .

# Run Inity in container
docker run -it --rm -v $(pwd):/workspace inity create my-project
```

## 📦 Package Manager Installation

### Homebrew (macOS/Linux)
```bash
# Coming soon
brew install inity
```

### Chocolatey (Windows)
```bash
# Coming soon  
choco install inity
```

### Snap (Linux)
```bash
# Coming soon
sudo snap install inity
```

## 🔍 Verification

After installation, verify Inity is working:

```bash
# Check version
inity --version

# Show help
inity --help

# Create test project
inity create test-project --template basic
```

## 🚨 Troubleshooting

### Command not found
- Ensure Python and pip are in your PATH
- Restart your terminal after installation
- Check if `~/.local/bin` is in your PATH (Linux/macOS)

### Permission denied
```bash
# Linux/macOS: Use --user flag
pip install --user -e .

# Windows: Run PowerShell as Administrator
```

### Import errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### PATH issues (Linux/macOS)
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### PATH issues (Windows)
1. Open "Environment Variables" in System Settings
2. Add Python Scripts directory to PATH
3. Restart Command Prompt

## 🔄 Updating Inity

### One-command update
```bash
# Linux/macOS
curl -sSL https://raw.githubusercontent.com/theaathish/Inity/main/install.sh | bash

# Windows
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/theaathish/Inity/main/install.ps1'))
```

### Manual update
```bash
cd /path/to/Inity
git pull origin main
pip install -r requirements.txt
pip install -e .
```

## 🗑️ Uninstalling

```bash
# Remove package
pip uninstall inity

# Remove executable (if created)
rm /usr/local/bin/inity  # Linux/macOS
del %USERPROFILE%\inity.bat  # Windows
```

## 🤝 Getting Help

- **Documentation:** [GitHub Repository](https://github.com/theaathish/Inity)
- **Issues:** [GitHub Issues](https://github.com/theaathish/Inity/issues)
- **Discussions:** [GitHub Discussions](https://github.com/theaathish/Inity/discussions)

---

*© 2024 Strucureo. Developed by Aathish.*
