#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define variables
CHROOT_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")/chroot"
DEBIAN_MIRROR="http://deb.devuan.org/merged"
DISTRIBUTION="ceres"

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root"
    exit 1
fi

echo "Setting up debootstrap environment in $CHROOT_DIR for Devuan $DISTRIBUTION..."

# Install debootstrap if not already installed
if ! command -v debootstrap &> /dev/null; then
    echo "debootstrap not found. Installing..."
    apt update
    apt install -y debootstrap
fi

# Create the chroot directory if it doesn't exist
mkdir -p "$CHROOT_DIR"

# Run debootstrap
echo "Running debootstrap..."
debootstrap --arch=amd64 "$DISTRIBUTION" "$CHROOT_DIR" "$DEBIAN_MIRROR"

echo "Debootstrap environment setup complete."
echo "You can now chroot into the environment using: sudo chroot $CHROOT_DIR"