#!/bin/bash
# One-command installer for Inity
# Intelligent Python project environment setup tool
# Developed by Aathish at Strucureo
# Usage: curl -sSL https://raw.githubusercontent.com/theaathish/Inity/main/install.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Art banner
echo -e "${BLUE}"
cat << "EOF"
 ___       _ _         
|_ _|_ __ (_) |_ _   _ 
 | || '_ \| | __| | | |
 | || | | | | |_| |_| |
|___|_| |_|_|\__|\__, |
                 |___/ 
EOF
echo -e "${NC}"

echo -e "${PURPLE}Inity - Intelligent Python Project Setup Tool${NC}"
echo -e "${CYAN}Developed by Aathish at Strucureo${NC}"
echo "=================================================="

# Detect OS
OS="$(uname -s)"
ARCH="$(uname -m)"

echo -e "${BLUE}🔍 Detecting system...${NC}"
echo "OS: $OS"
echo "Architecture: $ARCH"

# Set installation directory
if [[ "$OS" == "Darwin" ]]; then
    INSTALL_DIR="/usr/local/bin"
    PLATFORM="macos"
elif [[ "$OS" == "Linux" ]]; then
    if [ -w "/usr/local/bin" ]; then
        INSTALL_DIR="/usr/local/bin"
    elif [ -w "$HOME/.local/bin" ]; then
        INSTALL_DIR="$HOME/.local/bin"
        mkdir -p "$INSTALL_DIR"
    else
        INSTALL_DIR="$HOME/bin"
        mkdir -p "$INSTALL_DIR"
    fi
    PLATFORM="linux"
else
    echo -e "${RED}❌ Unsupported operating system: $OS${NC}"
    echo "Please use Windows installer or install manually"
    exit 1
fi

echo -e "${BLUE}📂 Installation directory: $INSTALL_DIR${NC}"

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python is not installed or not in PATH${NC}"
    echo "Please install Python 3.8+ first:"
    if [[ "$OS" == "Darwin" ]]; then
        echo "  brew install python"
    elif [[ "$OS" == "Linux" ]]; then
        echo "  sudo apt install python3 python3-pip python3-venv  # Ubuntu/Debian"
        echo "  sudo yum install python3 python3-pip  # CentOS/RHEL"
    fi
    exit 1
fi

# Get Python command
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo -e "${GREEN}✅ Python found: $($PYTHON_CMD --version)${NC}"

# Check if we need to handle externally managed environment
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
IS_EXTERNALLY_MANAGED=false

# Check for externally managed environment (common in newer Ubuntu/Debian)
if [[ "$OS" == "Linux" ]] && $PYTHON_CMD -c "import sysconfig; print(sysconfig.get_path('stdlib'))" 2>/dev/null | grep -q "/usr/lib"; then
    if [ -f "/usr/share/doc/python${PYTHON_VERSION}/README.venv" ] || [ -f "/usr/lib/python${PYTHON_VERSION}/EXTERNALLY-MANAGED" ]; then
        IS_EXTERNALLY_MANAGED=true
    fi
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo -e "${BLUE}📥 Downloading Inity...${NC}"

# Download and install directly from git
if command -v git &> /dev/null; then
    echo "Using git to clone repository..."
    git clone https://github.com/theaathish/Inity.git
    cd Inity
else
    echo "Downloading as zip archive..."
    if command -v curl &> /dev/null; then
        curl -L https://github.com/theaathish/Inity/archive/main.zip -o inity.zip
    elif command -v wget &> /dev/null; then
        wget https://github.com/theaathish/Inity/archive/main.zip -O inity.zip
    else
        echo -e "${RED}❌ Neither curl nor wget found. Please install one of them.${NC}"
        exit 1
    fi
    
    if command -v unzip &> /dev/null; then
        unzip inity.zip
        cd Inity-main
    else
        echo -e "${RED}❌ unzip not found. Please install unzip.${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}🔧 Installing Inity...${NC}"

# Choose installation method based on system
if command -v pipx &> /dev/null; then
    echo "Using pipx for isolated installation..."
    pipx install .
    INSTALL_SUCCESS=$?
elif [[ "$IS_EXTERNALLY_MANAGED" == "true" ]]; then
    echo "Detected externally managed Python environment..."
    echo "Creating isolated virtual environment for Inity..."
    
    # Create a dedicated venv for Inity
    INITY_VENV="$HOME/.local/share/inity-venv"
    mkdir -p "$(dirname "$INITY_VENV")"
    
    $PYTHON_CMD -m venv "$INITY_VENV"
    
    # Install in the virtual environment
    "$INITY_VENV/bin/pip" install --upgrade pip
    "$INITY_VENV/bin/pip" install -r requirements.txt
    "$INITY_VENV/bin/pip" install .
    
    # Create wrapper script
    cat > "$INSTALL_DIR/inity" << EOL
#!/bin/bash
# Inity wrapper script
# Developed by Aathish at Strucureo
exec "$INITY_VENV/bin/python" -m smartenv.main "\$@"
EOL
    
    chmod +x "$INSTALL_DIR/inity"
    INSTALL_SUCCESS=0
    
else
    echo "Using pip with user installation..."
    # Try different pip installation methods
    if $PYTHON_CMD -m pip install --user -r requirements.txt && $PYTHON_CMD -m pip install --user .; then
        INSTALL_SUCCESS=0
    elif $PYTHON_CMD -m pip install --user --break-system-packages -r requirements.txt && $PYTHON_CMD -m pip install --user --break-system-packages .; then
        INSTALL_SUCCESS=0
    else
        echo -e "${YELLOW}⚠️ Standard pip installation failed. Creating isolated installation...${NC}"
        
        # Create a dedicated venv for Inity
        INITY_VENV="$HOME/.local/share/inity-venv"
        mkdir -p "$(dirname "$INITY_VENV")"
        
        $PYTHON_CMD -m venv "$INITY_VENV"
        
        # Install in the virtual environment
        "$INITY_VENV/bin/pip" install --upgrade pip
        "$INITY_VENV/bin/pip" install -r requirements.txt
        "$INITY_VENV/bin/pip" install .
        
        # Create wrapper script
        cat > "$INSTALL_DIR/inity" << EOL
#!/bin/bash
# Inity wrapper script
# Developed by Aathish at Strucureo
exec "$INITY_VENV/bin/python" -m smartenv.main "\$@"
EOL
        
        chmod +x "$INSTALL_DIR/inity"
        INSTALL_SUCCESS=0
    fi
fi

# Cleanup
cd /
rm -rf "$TEMP_DIR"

if [ $INSTALL_SUCCESS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Inity installed successfully!${NC}"
    echo ""
    
    # Check if installation directory is in PATH
    if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
        echo -e "${YELLOW}⚠️  Warning: $INSTALL_DIR is not in your PATH${NC}"
        echo "Add this line to your ~/.bashrc or ~/.zshrc:"
        echo "export PATH=\"$INSTALL_DIR:\$PATH\""
        echo ""
        echo "Then run: source ~/.bashrc  (or restart your terminal)"
        echo ""
    fi
    
    echo -e "${CYAN}🚀 Quick Start:${NC}"
    echo "  inity --help                    # Show help"
    echo "  inity create my-awesome-project # Create new project"
    echo "  inity package search fastapi    # Search packages"
    echo ""
    
    echo -e "${PURPLE}📚 Documentation: https://github.com/theaathish/Inity${NC}"
    echo -e "${PURPLE}🐛 Issues: https://github.com/theaathish/Inity/issues${NC}"
    echo ""
    
    # Test installation
    echo -e "${BLUE}🧪 Testing installation...${NC}"
    if command -v inity &> /dev/null; then
        echo -e "${GREEN}✅ Inity is ready to use!${NC}"
        inity --version
    else
        echo -e "${YELLOW}⚠️  Inity installed but not in current PATH${NC}"
        echo "You may need to restart your terminal or update your PATH"
        echo "Or run: export PATH=\"$INSTALL_DIR:\$PATH\""
    fi
    
    echo ""
    echo -e "${CYAN}Happy coding with Inity! 🐍✨${NC}"
else
    echo -e "${RED}❌ Installation failed${NC}"
    echo "Please check the error messages above and try manual installation:"
    echo "  git clone https://github.com/theaathish/Inity.git"
    echo "  cd Inity"
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo "  pip install ."
    exit 1
fi
