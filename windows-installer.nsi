; NSIS Installer Script for Inity
; Intelligent Python project environment setup tool
; Developed by Aathish at Strucureo

!define PRODUCT_NAME "Inity"
!define PRODUCT_VERSION "0.3.2"
!define PRODUCT_PUBLISHER "Strucureo"
!define PRODUCT_WEB_SITE "https://github.com/theaathish/Inity"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\inity.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"

; Modern UI
!include "MUI2.nsh"
!include "x64.nsh"

; General
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "Inity-${PRODUCT_VERSION}-Windows-Installer.exe"
InstallDir "$PROGRAMFILES\Inity"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; Modern UI Configuration
!define MUI_ABORTWARNING
!define MUI_ICON "assets\inity.ico"
!define MUI_UNICON "assets\inity.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME

; License page
!insertmacro MUI_PAGE_LICENSE "LICENSE"

; Components page
!insertmacro MUI_PAGE_COMPONENTS

; Directory page
!insertmacro MUI_PAGE_DIRECTORY

; Instfiles page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\inity.exe"
!define MUI_FINISHPAGE_RUN_PARAMETERS "--help"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; Version Info
VIProductVersion "${PRODUCT_VERSION}.0"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "Comments" "Intelligent Python project environment setup tool"
VIAddVersionKey "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey "LegalTrademarks" "${PRODUCT_NAME} is a trademark of ${PRODUCT_PUBLISHER}"
VIAddVersionKey "LegalCopyright" "© 2024 ${PRODUCT_PUBLISHER}"
VIAddVersionKey "FileDescription" "${PRODUCT_NAME} Installer"
VIAddVersionKey "FileVersion" "${PRODUCT_VERSION}"

; Installer sections
Section "Inity Core" SecCore
  SectionIn RO
  
  ; Set output path to the installation directory
  SetOutPath "$INSTDIR"
  
  ; Check if Python is installed
  ReadRegStr $R0 HKLM "SOFTWARE\Python\PythonCore\3.12\InstallPath" ""
  StrCmp $R0 "" 0 PythonFound
  ReadRegStr $R0 HKLM "SOFTWARE\Python\PythonCore\3.11\InstallPath" ""
  StrCmp $R0 "" 0 PythonFound
  ReadRegStr $R0 HKLM "SOFTWARE\Python\PythonCore\3.10\InstallPath" ""
  StrCmp $R0 "" 0 PythonFound
  ReadRegStr $R0 HKLM "SOFTWARE\Python\PythonCore\3.9\InstallPath" ""
  StrCmp $R0 "" 0 PythonFound
  ReadRegStr $R0 HKLM "SOFTWARE\Python\PythonCore\3.8\InstallPath" ""
  StrCmp $R0 "" NoPython PythonFound
  
  NoPython:
    MessageBox MB_YESNO "Python 3.8+ is required but not found. Do you want to download Python?" IDYES DownloadPython IDNO SkipPython
    DownloadPython:
      ExecShell "open" "https://python.org/downloads/"
      MessageBox MB_OK "Please install Python and run this installer again."
      Abort
    SkipPython:
      MessageBox MB_OK "Inity requires Python 3.8+. Installation will continue but may not work properly."
  
  PythonFound:
  
  ; Copy files
  File /r "dist\*"
  File "README.md"
  File "LICENSE"
  
  ; Create virtual environment and install Inity
  DetailPrint "Creating virtual environment..."
  nsExec::ExecToLog 'python -m venv "$INSTDIR\venv"'
  
  DetailPrint "Installing Inity..."
  nsExec::ExecToLog '"$INSTDIR\venv\Scripts\pip.exe" install "$INSTDIR\inity-*.whl"'
  
  ; Create main executable wrapper
  FileOpen $4 "$INSTDIR\inity.exe" w
  FileWrite $4 "@echo off$\r$\n"
  FileWrite $4 '"$INSTDIR\venv\Scripts\python.exe" -m smartenv.main %*$\r$\n'
  FileClose $4
  
  ; Registry entries
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\inity.exe"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\inity.exe"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Add to PATH" SecPath
  ; Add to system PATH
  ReadRegStr $R0 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "PATH"
  StrCmp $R0 "" AddToPath 0
  StrStr $R1 $R0 "$INSTDIR"
  StrCmp $R1 "" 0 PathExists
  
  AddToPath:
    DetailPrint "Adding Inity to system PATH..."
    WriteRegExpandStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "PATH" "$R0;$INSTDIR"
    SendMessage ${HWND_BROADCAST} ${WM_WININICHANGE} 0 "STR:Environment" /TIMEOUT=5000
  PathExists:
SectionEnd

Section "Desktop Shortcut" SecDesktop
  CreateShortCut "$DESKTOP\Inity.lnk" "$INSTDIR\inity.exe" "--help" "$INSTDIR\inity.exe" 0
SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
  CreateDirectory "$SMPROGRAMS\Inity"
  CreateShortCut "$SMPROGRAMS\Inity\Inity.lnk" "$INSTDIR\inity.exe" "" "$INSTDIR\inity.exe" 0
  CreateShortCut "$SMPROGRAMS\Inity\Inity Help.lnk" "$INSTDIR\inity.exe" "--help" "$INSTDIR\inity.exe" 0
  CreateShortCut "$SMPROGRAMS\Inity\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "Installs Inity core files and Python virtual environment"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecPath} "Adds Inity to system PATH for global access"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Creates desktop shortcut"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} "Creates start menu shortcuts"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller section
Section Uninstall
  ; Remove files
  RMDir /r "$INSTDIR\venv"
  RMDir /r "$INSTDIR\dist"
  Delete "$INSTDIR\inity.exe"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\LICENSE"
  Delete "$INSTDIR\uninstall.exe"
  RMDir "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$DESKTOP\Inity.lnk"
  RMDir /r "$SMPROGRAMS\Inity"
  
  ; Remove from PATH
  ReadRegStr $R0 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "PATH"
  StrStr $R1 $R0 ";$INSTDIR"
  StrCmp $R1 "" CheckStart 0
  StrLen $R2 ";$INSTDIR"
  StrCpy $R3 $R1 "" $R2
  StrCpy $R4 $R0 $R1
  StrCpy $R0 "$R4$R3"
  Goto UpdatePath
  
  CheckStart:
    StrStr $R1 $R0 "$INSTDIR;"
    StrCmp $R1 "" CheckOnly 0
    StrLen $R2 "$INSTDIR;"
    StrCpy $R3 $R1 "" $R2
    StrCpy $R4 $R0 $R1
    StrCpy $R0 "$R4$R3"
    Goto UpdatePath
  
  CheckOnly:
    StrCmp $R0 "$INSTDIR" 0 UpdatePath
    StrCpy $R0 ""
  
  UpdatePath:
    WriteRegExpandStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "PATH" "$R0"
    SendMessage ${HWND_BROADCAST} ${WM_WININICHANGE} 0 "STR:Environment" /TIMEOUT=5000
  
  ; Remove registry entries
  DeleteRegKey HKLM "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
SectionEnd
