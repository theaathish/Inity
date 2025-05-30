# One-command installer for Inity on Windows
# Intelligent Python project environment setup tool
# Developed by Aathish at Strucureo
# Usage: iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/theaathish/Inity/main/install.ps1'))

$ErrorActionPreference = "Stop"

# Colors
$Red = [System.ConsoleColor]::Red
$Green = [System.ConsoleColor]::Green  
$Yellow = [System.ConsoleColor]::Yellow
$Blue = [System.ConsoleColor]::Blue
$Purple = [System.ConsoleColor]::Magenta
$Cyan = [System.ConsoleColor]::Cyan

function Write-ColorText {
    param($Text, $Color)
    $prevColor = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $Color
    Write-Host $Text
    $Host.UI.RawUI.ForegroundColor = $prevColor
}

function Find-PythonInstallation {
    Write-ColorText "Searching for Python installations..." $Blue
    
    # Common Python installation paths
    $pythonPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
        "$env:ProgramFiles\Python*\python.exe",
        "$env:ProgramFiles(x86)\Python*\python.exe",
        "$env:USERPROFILE\AppData\Local\Programs\Python\Python*\python.exe",
        "$env:USERPROFILE\anaconda3\python.exe",
        "$env:USERPROFILE\miniconda3\python.exe",
        "$env:ProgramData\Anaconda3\python.exe",
        "$env:ProgramData\Miniconda3\python.exe",
        "C:\Python*\python.exe"
    )
    
    $foundPythons = @()
    
    foreach ($pattern in $pythonPaths) {
        $matches = Get-ChildItem $pattern -ErrorAction SilentlyContinue | Where-Object { $_.Exists }
        foreach ($match in $matches) {
            try {
                $version = & $match.FullName --version 2>&1
                if ($version -match "Python (\d+\.\d+)") {
                    $versionNumber = [Version]$matches[1]
                    if ($versionNumber -ge [Version]"3.8") {
                        $foundPythons += @{
                            Path = $match.FullName
                            Version = $version.Trim()
                            VersionNumber = $versionNumber
                        }
                    }
                }
            } catch {
                # Skip invalid Python installations
            }
        }
    }
    
    # Check Windows Store Python
    try {
        $storePython = Get-Command python.exe -ErrorAction SilentlyContinue
        if ($storePython -and $storePython.Source -like "*WindowsApps*") {
            $version = & python.exe --version 2>&1
            if ($version -match "Python (\d+\.\d+)") {
                $versionNumber = [Version]$matches[1]
                if ($versionNumber -ge [Version]"3.8") {
                    $foundPythons += @{
                        Path = "python.exe"
                        Version = $version.Trim()
                        VersionNumber = $versionNumber
                        IsWindowsStore = $true
                    }
                }
            }
        }
    } catch {
        # Skip Windows Store Python if not accessible
    }
    
    if ($foundPythons.Count -eq 0) {
        return $null
    }
    
    # Return the newest version
    $bestPython = $foundPythons | Sort-Object VersionNumber -Descending | Select-Object -First 1
    return $bestPython
}

function Add-PythonToPath {
    param($PythonPath)
    
    if ($PythonPath -eq "python.exe") {
        # Windows Store Python is already in PATH
        return $true
    }
    
    $pythonDir = Split-Path $PythonPath
    $scriptsDir = Join-Path $pythonDir "Scripts"
    
    try {
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        $pathsToAdd = @()
        
        if (-not $currentPath.Contains($pythonDir)) {
            $pathsToAdd += $pythonDir
        }
        
        if ((Test-Path $scriptsDir) -and (-not $currentPath.Contains($scriptsDir))) {
            $pathsToAdd += $scriptsDir
        }
        
        if ($pathsToAdd.Count -gt 0) {
            $newPath = if ($currentPath) { "$currentPath;" + ($pathsToAdd -join ";") } else { $pathsToAdd -join ";" }
            [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
            
            # Update current session PATH
            $env:PATH = "$env:PATH;" + ($pathsToAdd -join ";")
            
            Write-ColorText "Added Python to PATH: $($pathsToAdd -join ', ')" $Green
            return $true
        }
        
        return $true
    } catch {
        Write-ColorText "Could not add Python to PATH automatically" $Yellow
        return $false
    }
}

function Remove-ExistingInstallation {
    Write-ColorText "Checking for existing Inity installations..." $Blue
    
    # Check for existing virtual environment
    $inityVenv = Join-Path $env:LOCALAPPDATA "inity-venv"
    if (Test-Path $inityVenv) {
        Write-ColorText "Removing existing virtual environment..." $Yellow
        Remove-Item $inityVenv -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    # Check for existing batch file
    $userPath = [Environment]::GetFolderPath('UserProfile')
    $batchPath = Join-Path $userPath "inity.bat"
    if (Test-Path $batchPath) {
        Write-ColorText "Removing existing launcher..." $Yellow
        Remove-Item $batchPath -Force -ErrorAction SilentlyContinue
    }
    
    # Check for pip-installed inity and remove it
    try {
        $pipList = & pip list 2>&1 | Select-String "inity"
        if ($pipList) {
            Write-ColorText "Removing existing pip installation..." $Yellow
            & pip uninstall inity -y 2>&1 | Out-Null
        }
    } catch {
        # Ignore errors if pip list fails
    }
    
    # Check for system-wide installation in Program Files
    $programFilesPath = "$env:ProgramFiles\Inity"
    if (Test-Path $programFilesPath) {
        Write-ColorText "Found system-wide installation. Attempting to remove..." $Yellow
        try {
            # Try to run uninstaller if it exists
            $uninstaller = Join-Path $programFilesPath "uninstall.exe"
            if (Test-Path $uninstaller) {
                Start-Process $uninstaller -ArgumentList "/S" -Wait
            } else {
                # Manual removal
                Remove-Item $programFilesPath -Recurse -Force -ErrorAction SilentlyContinue
            }
        } catch {
            Write-ColorText "Could not remove system installation. You may need to uninstall manually." $Yellow
        }
    }
    
    # Remove from PATH if present
    try {
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($currentPath -and $currentPath.Contains($userPath)) {
            $newPath = $currentPath.Replace(";$userPath", "").Replace("$userPath;", "").Replace($userPath, "")
            [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        }
    } catch {
        # Ignore PATH cleanup errors
    }
    
    Write-ColorText "Cleanup completed." $Green
}

# Art banner
Write-ColorText " ___       _ _         " $Blue
Write-ColorText "|_ _|_ __ (_) |_ _   _ " $Blue
Write-ColorText " | || '_ \| | __| | | |" $Blue
Write-ColorText " | || | | | | |_| |_| |" $Blue
Write-ColorText "|___|_| |_|_|\__|\__, |" $Blue
Write-ColorText "                 |___/ " $Blue

Write-Host ""
Write-ColorText "Inity - Intelligent Python Project Setup Tool" $Purple
Write-ColorText "Developed by Aathish at Strucureo" $Cyan
Write-Host "=================================================="

Write-ColorText "Detecting system..." $Blue
Write-Host "OS: Windows"
Write-Host ("PowerShell: " + $PSVersionTable.PSVersion)

# Remove any existing installations first
Remove-ExistingInstallation

# Check if Python is available in PATH first
$pythonFound = $false
$pythonPath = $null

try {
    $pythonVersion = & python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+)") {
        $versionNumber = [Version]$matches[1]
        if ($versionNumber -ge [Version]"3.8") {
            Write-ColorText ("Python found in PATH: " + $pythonVersion) $Green
            $pythonFound = $true
            $pythonPath = "python"
        } else {
            Write-ColorText ("Python version too old: " + $pythonVersion) $Yellow
        }
    }
} catch {
    # Python not in PATH, continue searching
}

# If Python not found in PATH, search the system
if (-not $pythonFound) {
    Write-ColorText "Python not found in PATH. Searching system..." $Yellow
    
    $foundPython = Find-PythonInstallation
    
    if ($foundPython) {
        Write-ColorText ("Found Python installation: " + $foundPython.Version + " at " + $foundPython.Path) $Green
        
        # Ask user if they want to add it to PATH
        Write-Host ""
        Write-ColorText "Would you like to add Python to your PATH for system-wide access? (y/n): " $Cyan -NoNewline
        $response = Read-Host
        
        if ($response -match "^[Yy]") {
            if (Add-PythonToPath $foundPython.Path) {
                $pythonPath = if ($foundPython.Path -eq "python.exe") { "python" } else { $foundPython.Path }
                $pythonFound = $true
                Write-ColorText "Python is now available system-wide!" $Green
            } else {
                $pythonPath = $foundPython.Path
                $pythonFound = $true
                Write-ColorText "Using Python directly from: $($foundPython.Path)" $Green
            }
        } else {
            $pythonPath = $foundPython.Path
            $pythonFound = $true
            Write-ColorText "Using Python directly from: $($foundPython.Path)" $Green
        }
    }
}

# If still no Python found, offer to install
if (-not $pythonFound) {
    Write-ColorText "Python 3.8+ is required but not found on this system." $Red
    Write-Host ""
    Write-ColorText "Would you like to:" $Cyan
    Write-Host "1. Download and install Python automatically"
    Write-Host "2. Open Python download page manually"
    Write-Host "3. Exit and install Python manually"
    Write-Host ""
    Write-ColorText "Choose option (1/2/3): " $Cyan -NoNewline
    $choice = Read-Host
    
    switch ($choice) {
        "1" {
            Write-ColorText "Downloading Python installer..." $Blue
            try {
                $pythonUrl = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
                $installerPath = Join-Path $env:TEMP "python-installer.exe"
                
                Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath
                
                Write-ColorText "Running Python installer..." $Blue
                Write-Host "Please follow the installer and make sure to check 'Add Python to PATH'"
                
                Start-Process $installerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
                
                # Refresh PATH
                $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
                
                # Check if installation was successful
                try {
                    $pythonVersion = & python --version 2>&1
                    Write-ColorText ("Python installed successfully: " + $pythonVersion) $Green
                    $pythonFound = $true
                    $pythonPath = "python"
                } catch {
                    Write-ColorText "Python installation may not be complete. Please restart your terminal." $Yellow
                    Read-Host "Press Enter to exit"
                    exit 1
                }
            } catch {
                Write-ColorText "Failed to download/install Python automatically." $Red
                Write-ColorText "Please install Python manually from https://python.org" $Yellow
                Read-Host "Press Enter to exit"
                exit 1
            }
        }
        "2" {
            Write-ColorText "Opening Python download page..." $Blue
            Start-Process "https://python.org/downloads/"
            Write-Host "Please install Python and run this installer again."
            Read-Host "Press Enter to exit"
            exit 1
        }
        default {
            Write-Host "Please install Python 3.8+ from https://python.org"
            Write-Host "Make sure to check 'Add Python to PATH' during installation"
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
}

# Check if pip is available
try {
    if ($pythonPath -eq "python") {
        $pipVersion = & pip --version 2>&1
    } else {
        $pipPath = Join-Path (Split-Path $pythonPath) "Scripts\pip.exe"
        if (Test-Path $pipPath) {
            $pipVersion = & $pipPath --version 2>&1
        } else {
            # Try using python -m pip
            $pipVersion = & $pythonPath -m pip --version 2>&1
        }
    }
    Write-ColorText ("pip found: " + $pipVersion) $Green
} catch {
    Write-ColorText "pip is not available. Installing pip..." $Yellow
    try {
        & $pythonPath -m ensurepip --upgrade
        Write-ColorText "pip installed successfully" $Green
    } catch {
        Write-ColorText "Failed to install pip" $Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Create temporary directory
$tempDir = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_ }
Set-Location $tempDir

Write-ColorText "Downloading Inity..." $Blue

# Download Inity
try {
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Write-Host "Using git to clone repository..."
        & git clone https://github.com/theaathish/Inity.git
        Set-Location Inity
    } else {
        Write-Host "Downloading as zip archive..."
        $zipPath = Join-Path $tempDir "inity.zip"
        Invoke-WebRequest -Uri "https://github.com/theaathish/Inity/archive/main.zip" -OutFile $zipPath
        Expand-Archive -Path $zipPath -DestinationPath $tempDir
        Set-Location "Inity-main"
    }
} catch {
    Write-ColorText ("Failed to download Inity: " + $_.Exception.Message) $Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-ColorText "Installing Inity..." $Blue

try {
    # Create fresh isolated virtual environment for Inity on Windows
    Write-Host "Creating fresh isolated virtual environment for Inity..."
    $inityVenv = Join-Path $env:LOCALAPPDATA "inity-venv"
    
    # Ensure clean installation directory
    if (Test-Path $inityVenv) {
        Remove-Item $inityVenv -Recurse -Force
    }
    
    # Create new virtual environment using the found Python
    & $pythonPath -m venv $inityVenv
    
    # Get the correct paths for the virtual environment
    $venvPython = Join-Path $inityVenv "Scripts\python.exe"
    $venvPip = Join-Path $inityVenv "Scripts\pip.exe"
    
    # Install in the virtual environment
    Write-Host "Installing dependencies in virtual environment..."
    & $venvPip install --upgrade pip
    & $venvPip install -r requirements.txt
    & $venvPip install .
    
    # Create wrapper batch file in user directory
    $batchContent = "@echo off" + [Environment]::NewLine + "`"$venvPython`" -m smartenv.main %*"
    
    $userPath = [Environment]::GetFolderPath('UserProfile')
    $batchPath = Join-Path $userPath "inity.bat"
    $batchContent | Out-File -FilePath $batchPath -Encoding ASCII
    
    # Add to user PATH if not already present
    try {
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if (-not $currentPath.Contains($userPath)) {
            $newPath = if ($currentPath) { "$currentPath;$userPath" } else { $userPath }
            [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
            Write-ColorText "Added to user PATH for easy access" $Green
        }
    } catch {
        Write-ColorText "Could not add to PATH automatically" $Yellow
    }
    
    Write-ColorText "Inity installed successfully!" $Green
    
} catch {
    Write-ColorText ("Installation failed: " + $_.Exception.Message) $Red
    Write-Host "Error details: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Manual installation instructions:"
    Write-Host "1. Install Python from https://python.org"
    Write-Host "2. Open Command Prompt and run:"
    Write-Host "   git clone https://github.com/theaathish/Inity.git"
    Write-Host "   cd Inity"
    Write-Host "   python -m venv .venv"
    Write-Host "   .venv\Scripts\activate"
    Write-Host "   pip install -r requirements.txt"
    Write-Host "   pip install ."
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-ColorText "Inity installed successfully!" $Green
Write-Host ""

Write-ColorText ("Created launcher: " + $batchPath) $Blue
Write-ColorText "Inity has been added to your PATH" $Green
Write-Host "You can now use 'inity' from any Command Prompt or PowerShell window"
Write-Host ""

Write-ColorText "Quick Start:" $Cyan
Write-Host "  inity --help                    # Show help"
Write-Host "  inity create my-awesome-project # Create new project"
Write-Host "  inity package search fastapi    # Search packages"
Write-Host ""

Write-ColorText "Documentation: https://github.com/theaathish/Inity" $Purple
Write-ColorText "Issues: https://github.com/theaathish/Inity/issues" $Purple
Write-Host ""

# Test installation
Write-ColorText "Testing installation..." $Blue
try {
    $testOutput = & $batchPath --version 2>&1
    Write-ColorText ("Inity is ready to use! " + $testOutput) $Green
} catch {
    Write-ColorText "Installation completed but test failed" $Yellow
    Write-Host "You may need to restart your command prompt"
}

# Cleanup
Set-Location $env:TEMP
Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-ColorText "Happy coding with Inity!" $Cyan
Write-Host ""
Write-Host "Installation complete. Press Enter to continue..."
Read-Host
