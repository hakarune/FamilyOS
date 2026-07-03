@echo off
SETLOCAL

REM Define variables
SET "CHROOT_DIR=%~dp0..\chroot"
SET "DEBIAN_MIRROR=http://deb.devuan.org/merged"
SET "DISTRIBUTION=daedalus"

REM Check if running as administrator
NET SESSION >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO This script must be run as Administrator.
    GOTO :EOF
)

ECHO Setting up debootstrap environment in %CHROOT_DIR% for Devuan %DISTRIBUTION%...

REM Check for WSL and debootstrap
ECHO Checking for Windows Subsystem for Linux (WSL)...
wsl.exe -l -q >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO WSL is not installed or not configured. Please install WSL and a Linux distribution (e.g., Debian or Ubuntu) first.
    GOTO :EOF
)

ECHO WSL is installed. Attempting to install debootstrap inside WSL...
REM Execute debootstrap setup inside WSL
wsl.exe bash -c "\
    if ! command -v debootstrap > /dev/null; then \
        echo \"debootstrap not found. Installing...\"; \
        sudo apt update && sudo apt install -y debootstrap; \
    fi; \
    mkdir -p \"$(wslpath -a ",CHROOT_DIR,")\"; \
    sudo debootstrap --arch=amd64 ",DISTRIBUTION," \"$(wslpath -a ",CHROOT_DIR,")\" ",DEBIAN_MIRROR," \
"

IF %ERRORLEVEL% NEQ 0 (
    ECHO Failed to run debootstrap in WSL. Please check your WSL installation and internet connection.
    GOTO :EOF
)

ECHO Debootstrap environment setup complete.
ECHO You can now access the chroot environment via WSL. For example: wsl.exe -d Debian bash -c \"sudo chroot \"$(wslpath -a ",CHROOT_DIR,")\"\"

ENDLOCAL
