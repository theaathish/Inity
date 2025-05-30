"""
Build Windows installer for Inity
Developed by Aathish at Strucureo
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """Check if required tools are available."""
    print("🔍 Checking requirements...")
    
    # Check for NSIS
    nsis_paths = [
        "C:\\Program Files (x86)\\NSIS\\makensis.exe",
        "C:\\Program Files\\NSIS\\makensis.exe",
        "makensis.exe"  # If in PATH
    ]
    
    nsis_exe = None
    for path in nsis_paths:
        if shutil.which(path) or os.path.exists(path):
            nsis_exe = path
            break
    
    if not nsis_exe:
        print("❌ NSIS not found. Please install NSIS from https://nsis.sourceforge.io/")
        print("After installation, make sure makensis.exe is in your PATH")
        return False, None
    
    print(f"✅ NSIS found: {nsis_exe}")
    return True, nsis_exe

def build_executable():
    """Build the executable first."""
    print("🏗️ Building executable...")
    
    try:
        subprocess.run([sys.executable, "build.py"], check=True)
        print("✅ Executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build executable: {e}")
        return False

def create_wheel():
    """Create wheel distribution."""
    print("📦 Creating wheel distribution...")
    
    try:
        subprocess.run([sys.executable, "setup.py", "bdist_wheel"], check=True)
        print("✅ Wheel created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create wheel: {e}")
        return False

def prepare_installer_files():
    """Prepare files for installer."""
    print("📁 Preparing installer files...")
    
    installer_dir = Path("installer")
    installer_dir.mkdir(exist_ok=True)
    
    # Copy executable
    if Path("dist/inity.exe").exists():
        shutil.copy2("dist/inity.exe", installer_dir)
    
    # Copy wheel files
    dist_dir = Path("dist")
    for wheel_file in dist_dir.glob("*.whl"):
        shutil.copy2(wheel_file, installer_dir)
    
    # Copy documentation
    for doc_file in ["README.md", "LICENSE"]:
        if Path(doc_file).exists():
            shutil.copy2(doc_file, installer_dir)
    
    print("✅ Files prepared for installer")
    return True

def build_installer(nsis_exe):
    """Build the Windows installer."""
    print("🎁 Building Windows installer...")
    
    try:
        subprocess.run([nsis_exe, "windows-installer.nsi"], check=True)
        print("✅ Windows installer built successfully")
        
        # Find the generated installer
        installer_files = list(Path(".").glob("Inity-*-Windows-Installer.exe"))
        if installer_files:
            installer_file = installer_files[0]
            size_mb = installer_file.stat().st_size / (1024 * 1024)
            print(f"📦 Installer: {installer_file} ({size_mb:.1f} MB)")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build installer: {e}")
        return False

def main():
    """Main build process."""
    print("🏗️ Inity Windows Installer Builder")
    print("Developed by Aathish at Strucureo")
    print("=" * 40)
    
    if sys.platform != "win32":
        print("❌ This script must be run on Windows")
        sys.exit(1)
    
    # Check requirements
    requirements_ok, nsis_exe = check_requirements()
    if not requirements_ok:
        sys.exit(1)
    
    # Build steps
    steps = [
        ("Building executable", build_executable),
        ("Creating wheel", create_wheel),
        ("Preparing files", prepare_installer_files),
        ("Building installer", lambda: build_installer(nsis_exe))
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Failed: {step_name}")
            sys.exit(1)
    
    print("\n🎉 Windows installer built successfully!")
    print("\n📋 Installation Instructions:")
    print("1. Run the generated .exe file as Administrator")
    print("2. Follow the installation wizard")
    print("3. Choose components to install (PATH, shortcuts, etc.)")
    print("4. Inity will be available globally after installation")

if __name__ == "__main__":
    main()
