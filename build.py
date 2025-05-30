"""
Build script for Inity - Cross-platform Python project setup tool
Developed by Aathish at Strucureo
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def get_platform_info():
    """Get current platform information."""
    system = platform.system().lower()
    architecture = platform.machine().lower()
    
    if system == "windows":
        return "windows", "exe"
    elif system == "darwin":
        return "macos", ""
    elif system == "linux":
        return "linux", ""
    else:
        return system, ""

def clean_build_dirs():
    """Clean previous build directories."""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name}/")

def build_executable():
    """Build executable using PyInstaller."""
    platform_name, ext = get_platform_info()
    
    print(f"\n🚀 Building Inity for {platform_name}...")
    print("=" * 50)
    
    # PyInstaller command - Fixed syntax for cross-platform compatibility
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable
        "--name", "inity",              # Executable name
        "--console",                    # Console application
        "--clean",                      # Clean cache
        "--noconfirm",                  # Don't ask for confirmation
    ]
    
    # Add data files with correct platform-specific syntax
    if platform_name == "windows":
        cmd.extend(["--add-data", "smartenv;smartenv"])
    else:
        cmd.extend(["--add-data", "smartenv:smartenv"])
    
    # Add hidden imports
    hidden_imports = [
        "smartenv",
        "smartenv.commands",
        "smartenv.commands.create",
        "smartenv.commands.init",
        "smartenv.commands.templates", 
        "smartenv.commands.package",
        "smartenv.utils",
        "smartenv.utils.python_version",
        "smartenv.utils.package_search",
        "smartenv.utils.package_manager",
        "smartenv.utils.env_generator",
        "smartenv.utils.git_utils",
        "smartenv.core",
        "smartenv.core.project_creator",
        "smartenv.templates",
        "smartenv.templates.registry",
        "smartenv.templates.template",
    ]
    
    for import_name in hidden_imports:
        cmd.extend(["--hidden-import", import_name])
    
    # Platform-specific options (only if icon files exist)
    icon_path = None
    if platform_name == "windows" and os.path.exists("assets/inity.ico"):
        icon_path = "assets/inity.ico"
    elif platform_name == "macos" and os.path.exists("assets/inity.icns"):
        icon_path = "assets/inity.icns"
    
    if icon_path:
        cmd.extend(["--icon", icon_path])
    
    # Add entry point
    cmd.append("smartenv/main.py")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Build completed successfully!")
        
        # Show output location
        exe_name = f"inity{'.exe' if platform_name == 'windows' else ''}"
        exe_path = Path("dist") / exe_name
        
        if exe_path.exists():
            size = exe_path.stat().st_size / (1024 * 1024)  # Size in MB
            print(f"📦 Executable: {exe_path} ({size:.1f} MB)")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_installer():
    """Create platform-specific installer."""
    platform_name, ext = get_platform_info()
    
    if platform_name == "windows":
        create_windows_installer()
    elif platform_name == "macos":
        create_macos_installer()
    elif platform_name == "linux":
        create_linux_installer()

def create_windows_installer():
    """Create Windows installer using simple zip."""
    print("\n📦 Creating Windows installer...")
    
    import zipfile
    
    dist_dir = Path("dist")
    zip_path = dist_dir / "inity-windows.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(dist_dir / "inity.exe", "inity.exe")
        zipf.writestr("README.txt", """
Inity - Python Project Setup Tool
Developed by Aathish at Strucureo

Installation:
1. Extract inity.exe to a folder (e.g., C:\\Tools\\inity\\)
2. Add the folder to your PATH environment variable
3. Open Command Prompt and run: inity --help

Usage:
inity create my-project
inity package search requests
inity --help for more commands
""")
    
    print(f"✅ Windows distribution created: {zip_path}")

def create_macos_installer():
    """Create macOS installer."""
    print("\n📦 Creating macOS installer...")
    
    import zipfile
    
    dist_dir = Path("dist")
    zip_path = dist_dir / "inity-macos.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(dist_dir / "inity", "inity")
        # Fixed escape sequence by using raw string
        zipf.writestr("install.sh", r"""#!/bin/bash
# Inity installer for macOS
# Developed by Aathish at Strucureo

echo "Installing Inity..."

# Create installation directory
sudo mkdir -p /usr/local/bin

# Copy executable
sudo cp inity /usr/local/bin/inity
sudo chmod +x /usr/local/bin/inity

echo "✅ Inity installed successfully!"
echo "Run 'inity --help' to get started"
""")
        
        zipf.writestr("README.txt", """
Inity - Python Project Setup Tool
Developed by Aathish at Strucureo

Installation:
1. Extract the files
2. Run: chmod +x install.sh && ./install.sh
3. Or manually copy 'inity' to /usr/local/bin/

Usage:
inity create my-project
inity package search requests
inity --help for more commands
""")
    
    print(f"✅ macOS distribution created: {zip_path}")

def create_linux_installer():
    """Create Linux installer."""
    print("\n📦 Creating Linux installer...")
    
    import zipfile
    
    dist_dir = Path("dist")
    zip_path = dist_dir / "inity-linux.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(dist_dir / "inity", "inity")
        # Fixed escape sequence by using raw string
        zipf.writestr("install.sh", r"""#!/bin/bash
# Inity installer for Linux
# Developed by Aathish at Strucureo

echo "Installing Inity..."

# Detect installation directory
if [ -w "/usr/local/bin" ]; then
    INSTALL_DIR="/usr/local/bin"
elif [ -w "$HOME/.local/bin" ]; then
    INSTALL_DIR="$HOME/.local/bin"
    mkdir -p "$INSTALL_DIR"
else
    echo "Creating installation directory in home..."
    INSTALL_DIR="$HOME/bin"
    mkdir -p "$INSTALL_DIR"
    echo "Add $INSTALL_DIR to your PATH:"
    echo "echo 'export PATH=$INSTALL_DIR:\$PATH' >> ~/.bashrc"
fi

# Copy executable
cp inity "$INSTALL_DIR/inity"
chmod +x "$INSTALL_DIR/inity"

echo "✅ Inity installed to $INSTALL_DIR"
echo "Run 'inity --help' to get started"
""")
        
        zipf.writestr("README.txt", """
Inity - Python Project Setup Tool
Developed by Aathish at Strucureo

Installation:
1. Extract the files
2. Run: chmod +x install.sh && ./install.sh
3. Or manually copy 'inity' to a directory in your PATH

Usage:
inity create my-project
inity package search requests
inity --help for more commands
""")
    
    print(f"✅ Linux distribution created: {zip_path}")

def main():
    """Main build process."""
    print("🏗️  Inity Build System")
    print("Developed by Aathish at Strucureo")
    print("=" * 40)
    
    platform_name, ext = get_platform_info()
    print(f"Platform: {platform_name}")
    
    # Check if smartenv directory exists
    if not os.path.exists("smartenv"):
        print("❌ Error: 'smartenv' directory not found!")
        print("Make sure you're running this script from the project root directory.")
        sys.exit(1)
    
    # Check if main.py exists
    if not os.path.exists("smartenv/main.py"):
        print("❌ Error: 'smartenv/main.py' not found!")
        sys.exit(1)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build executable
    if build_executable():
        create_installer()
        print("\n🎉 Build process completed!")
        print(f"Check the 'dist/' directory for your {platform_name} distribution")
    else:
        print("\n❌ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
