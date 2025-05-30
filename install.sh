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

remove_existing_installation() {
    echo -e "${BLUE}🔍 Checking for existing Inity installations...${NC}"
    
    # Remove existing virtual environment
    INITY_VENV="$HOME/.local/share/inity-venv"
    if [ -d "$INITY_VENV" ]; then
        echo -e "${YELLOW}Removing existing virtual environment...${NC}"
        rm -rf "$INITY_VENV"
    fi
    
    # Remove existing executables from common locations
    COMMON_PATHS=("/usr/local/bin/inity" "$HOME/.local/bin/inity" "$HOME/bin/inity")
    for path in "${COMMON_PATHS[@]}"; do
        if [ -f "$path" ]; then
            echo -e "${YELLOW}Removing existing executable: $path${NC}"
            rm -f "$path"
        fi
    done
    
    # Remove pip-installed inity
    if command -v pip3 &> /dev/null; then
        if pip3 list | grep -i inity &> /dev/null; then
            echo -e "${YELLOW}Removing existing pip installation...${NC}"
            pip3 uninstall inity -y 2>/dev/null || true
        fi
    fi
    
    if command -v pip &> /dev/null; then
        if pip list | grep -i inity &> /dev/null; then
            echo -e "${YELLOW}Removing existing pip installation...${NC}"
            pip uninstall inity -y 2>/dev/null || true
        fi
    fi
    
    # Remove pipx installation
    if command -v pipx &> /dev/null; then
        if pipx list | grep -i inity &> /dev/null; then
            echo -e "${YELLOW}Removing existing pipx installation...${NC}"
            pipx uninstall inity 2>/dev/null || true
        fi
    fi
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

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

# Remove any existing installations first
remove_existing_installation

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
        echo "  sudo apt update"
        echo "  sudo apt install python3 python3-pip python3-venv python3-full  # Ubuntu/Debian"
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

# Check for required packages on Linux
if [[ "$OS" == "Linux" ]]; then
    echo -e "${BLUE}🔍 Checking for required packages...${NC}"
    
    # Check for python3-venv
    if ! $PYTHON_CMD -c "import venv" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  python3-venv is not installed${NC}"
        echo "Installing required packages..."
        
        # Detect package manager and install venv
        if command -v apt &> /dev/null; then
            echo "Using apt to install python3-venv..."
            if sudo apt update && sudo apt install -y python3-venv python3-full; then
                echo -e "${GREEN}✅ python3-venv installed successfully${NC}"
            else
                echo -e "${RED}❌ Failed to install python3-venv${NC}"
                echo "Please run manually: sudo apt install python3-venv python3-full"
                exit 1
            fi
        elif command -v yum &> /dev/null; then
            echo "Using yum to install python3-venv..."
            sudo yum install -y python3-venv
        elif command -v dnf &> /dev/null; then
            echo "Using dnf to install python3-venv..."
            sudo dnf install -y python3-venv
        else
            echo -e "${RED}❌ Cannot install python3-venv automatically${NC}"
            echo "Please install it manually:"
            echo "  Ubuntu/Debian: sudo apt install python3-venv python3-full"
            echo "  CentOS/RHEL: sudo yum install python3-venv"
            exit 1
        fi
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

# Always use isolated virtual environment approach for better compatibility
echo "Creating fresh isolated virtual environment for Inity..."

# Create a dedicated venv for Inity
INITY_VENV="$HOME/.local/share/inity-venv"
mkdir -p "$(dirname "$INITY_VENV")"

# Remove existing venv if it exists (double-check)
if [ -d "$INITY_VENV" ]; then
    echo "Ensuring clean installation directory..."
    rm -rf "$INITY_VENV"
fi

# Create new virtual environment
echo "Creating virtual environment at $INITY_VENV..."
if ! $PYTHON_CMD -m venv "$INITY_VENV"; then
    echo -e "${RED}❌ Failed to create virtual environment${NC}"
    echo "This usually means python3-venv is not installed."
    echo ""
    echo "Please install it:"
    if [[ "$OS" == "Linux" ]]; then
        echo "  Ubuntu/Debian: sudo apt install python3-venv python3-full"
        echo "  CentOS/RHEL: sudo yum install python3-venv"
    elif [[ "$OS" == "Darwin" ]]; then
        echo "  macOS: brew install python"
    fi
    exit 1
fi

# Install in the virtual environment
echo "Installing dependencies in fresh virtual environment..."
"$INITY_VENV/bin/pip" install --upgrade pip
"$INITY_VENV/bin/pip" install -r requirements.txt
"$INITY_VENV/bin/pip" install .

# Create wrapper script
echo "Creating fresh wrapper script..."
cat > "$INSTALL_DIR/inity" << EOL
#!/bin/bash
# Inity wrapper script
# Developed by Aathish at Strucureo

# Check if virtual environment exists
if [ ! -f "$INITY_VENV/bin/python" ]; then
    echo "Error: Inity virtual environment not found at $INITY_VENV"
    echo "Please reinstall Inity using:"
    echo "curl -sSL https://raw.githubusercontent.com/theaathish/Inity/main/install.sh | bash"
    exit 1
fi

# Execute Inity
exec "$INITY_VENV/bin/python" -m smartenv.main "\$@"
EOL

chmod +x "$INSTALL_DIR/inity"

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}🎉 Fresh Inity installation completed successfully!${NC}"
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
