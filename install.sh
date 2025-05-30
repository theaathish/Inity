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

find_python_installation() {
    echo -e "${BLUE}🔍 Searching for Python installations...${NC}"
    
    # Common Python installation paths
    local python_paths=(
        "/usr/bin/python3"
        "/usr/local/bin/python3"
        "/opt/python*/bin/python3"
        "/usr/bin/python"
        "/usr/local/bin/python"
        "$HOME/.pyenv/versions/*/bin/python"
        "$HOME/anaconda3/bin/python"
        "$HOME/miniconda3/bin/python"
        "/opt/anaconda3/bin/python"
        "/opt/miniconda3/bin/python"
        "/usr/local/anaconda3/bin/python"
        "/usr/local/miniconda3/bin/python"
    )
    
    local found_pythons=()
    
    for pattern in "${python_paths[@]}"; do
        for python_path in $pattern; do
            if [ -x "$python_path" ]; then
                local version=$("$python_path" --version 2>&1)
                if [[ $version =~ Python\ ([0-9]+)\.([0-9]+) ]]; then
                    local major=${BASH_REMATCH[1]}
                    local minor=${BASH_REMATCH[2]}
                    if [ "$major" -gt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -ge 8 ]); then
                        found_pythons+=("$python_path:$version")
                    fi
                fi
            fi
        done
    done
    
    if [ ${#found_pythons[@]} -eq 0 ]; then
        return 1
    fi
    
    # Return the first suitable Python found
    echo "${found_pythons[0]}"
    return 0
}

install_python_system() {
    echo -e "${BLUE}🔧 Installing Python...${NC}"
    
    if command -v apt &> /dev/null; then
        echo "Using apt to install Python..."
        if sudo apt update && sudo apt install -y python3 python3-pip python3-venv python3-full; then
            return 0
        fi
    elif command -v yum &> /dev/null; then
        echo "Using yum to install Python..."
        if sudo yum install -y python3 python3-pip python3-venv; then
            return 0
        fi
    elif command -v dnf &> /dev/null; then
        echo "Using dnf to install Python..."
        if sudo dnf install -y python3 python3-pip python3-venv; then
            return 0
        fi
    elif command -v pacman &> /dev/null; then
        echo "Using pacman to install Python..."
        if sudo pacman -S --noconfirm python python-pip; then
            return 0
        fi
    elif command -v brew &> /dev/null; then
        echo "Using brew to install Python..."
        if brew install python; then
            return 0
        fi
    fi
    
    return 1
}

add_python_to_path() {
    local python_path="$1"
    local python_dir=$(dirname "$python_path")
    
    # Check if already in PATH
    if [[ ":$PATH:" == *":$python_dir:"* ]]; then
        return 0
    fi
    
    # Add to appropriate shell config
    local shell_config=""
    if [ -n "$BASH_VERSION" ]; then
        shell_config="$HOME/.bashrc"
    elif [ -n "$ZSH_VERSION" ]; then
        shell_config="$HOME/.zshrc"
    else
        shell_config="$HOME/.profile"
    fi
    
    echo "export PATH=\"$python_dir:\$PATH\"" >> "$shell_config"
    export PATH="$python_dir:$PATH"
    
    echo -e "${GREEN}✅ Added Python to PATH in $shell_config${NC}"
    return 0
}

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

# Check if Python is available in PATH first
PYTHON_FOUND=false
PYTHON_CMD=""

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    if [[ $PYTHON_VERSION =~ Python\ ([0-9]+)\.([0-9]+) ]]; then
        MAJOR=${BASH_REMATCH[1]}
        MINOR=${BASH_REMATCH[2]}
        if [ "$MAJOR" -gt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 8 ]); then
            echo -e "${GREEN}✅ Python found in PATH: $PYTHON_VERSION${NC}"
            PYTHON_CMD="python3"
            PYTHON_FOUND=true
        else
            echo -e "${YELLOW}⚠️ Python version too old: $PYTHON_VERSION${NC}"
        fi
    fi
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION =~ Python\ ([0-9]+)\.([0-9]+) ]]; then
        MAJOR=${BASH_REMATCH[1]}
        MINOR=${BASH_REMATCH[2]}
        if [ "$MAJOR" -gt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 8 ]); then
            echo -e "${GREEN}✅ Python found in PATH: $PYTHON_VERSION${NC}"
            PYTHON_CMD="python"
            PYTHON_FOUND=true
        else
            echo -e "${YELLOW}⚠️ Python version too old: $PYTHON_VERSION${NC}"
        fi
    fi
fi

# If Python not found in PATH, search the system
if [ "$PYTHON_FOUND" = false ]; then
    echo -e "${YELLOW}⚠️ Python not found in PATH. Searching system...${NC}"
    
    if python_info=$(find_python_installation); then
        IFS=':' read -r python_path python_version <<< "$python_info"
        echo -e "${GREEN}✅ Found Python installation: $python_version at $python_path${NC}"
        
        # Ask user if they want to add it to PATH
        echo ""
        echo -e "${CYAN}Would you like to add Python to your PATH for system-wide access? (y/n): ${NC}"
        read -r response
        
        if [[ $response =~ ^[Yy] ]]; then
            if add_python_to_path "$python_path"; then
                PYTHON_CMD="python3"
                PYTHON_FOUND=true
                echo -e "${GREEN}✅ Python is now available system-wide!${NC}"
            else
                PYTHON_CMD="$python_path"
                PYTHON_FOUND=true
                echo -e "${GREEN}✅ Using Python directly from: $python_path${NC}"
            fi
        else
            PYTHON_CMD="$python_path"
            PYTHON_FOUND=true
            echo -e "${GREEN}✅ Using Python directly from: $python_path${NC}"
        fi
    fi
fi

# If still no Python found, offer to install
if [ "$PYTHON_FOUND" = false ]; then
    echo -e "${RED}❌ Python 3.8+ is required but not found on this system.${NC}"
    echo ""
    echo -e "${CYAN}Would you like to install Python automatically? (y/n): ${NC}"
    read -r response
    
    if [[ $response =~ ^[Yy] ]]; then
        if install_python_system; then
            echo -e "${GREEN}✅ Python installed successfully${NC}"
            # Recheck for Python
            if command -v python3 &> /dev/null; then
                PYTHON_CMD="python3"
                PYTHON_FOUND=true
            elif command -v python &> /dev/null; then
                PYTHON_CMD="python"
                PYTHON_FOUND=true
            fi
        else
            echo -e "${RED}❌ Failed to install Python automatically${NC}"
            echo "Please install Python manually:"
            if [[ "$OS" == "Darwin" ]]; then
                echo "  brew install python"
                echo "  or download from https://python.org"
            elif [[ "$OS" == "Linux" ]]; then
                echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv python3-full"
                echo "  CentOS/RHEL: sudo yum install python3 python3-pip python3-venv"
                echo "  or download from https://python.org"
            fi
            exit 1
        fi
    else
        echo "Please install Python 3.8+ and run this installer again"
        echo "Installation instructions:"
        if [[ "$OS" == "Darwin" ]]; then
            echo "  brew install python"
        elif [[ "$OS" == "Linux" ]]; then
            echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv python3-full"
            echo "  CentOS/RHEL: sudo yum install python3 python3-pip python3-venv"
        fi
        exit 1
    fi
fi

if [ "$PYTHON_FOUND" = false ]; then
    echo -e "${RED}❌ Could not find or install Python 3.8+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python found: $($PYTHON_CMD --version)${NC}"

# Check for required packages on Linux
if [[ "$OS" == "Linux" ]]; then
    echo -e "${BLUE}🔍 Checking for required packages...${NC}"
    
    # Check for python3-venv
    if ! $PYTHON_CMD -c "import venv" 2>/dev/null; then
        echo -e "${YELLOW}⚠️ python3-venv is not installed${NC}"
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

# Create new virtual environment using the found Python
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
