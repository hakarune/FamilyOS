#!/bin/sh
# Launches the FamilyOS kiosk session for the toddler user on X11 start.
#
# Install path for launcher/ is finalized during Phase 2 packaging;
# /opt/familyos/launcher is the assumed target for this scaffold.
exec python3 /opt/familyos/launcher/main.py
