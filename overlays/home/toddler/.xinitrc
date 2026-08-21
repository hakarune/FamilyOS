#!/bin/sh
# Launches the FamilyOS kiosk session for the toddler user on X11 start.
#
# Openbox runs as the window manager in the background; the FamilyOS
# Launcher runs in the foreground so the X session's lifetime is tied
# to it - if the launcher exits/crashes, the session ends and TTY1
# returns to a fresh autologin rather than leaving a bare WM running
# with nothing to interact with.
#
# Install path for launcher/ is finalized during Phase 2 packaging;
# /opt/familyos/launcher is the assumed target for this scaffold.
openbox &
exec python3 /opt/familyos/launcher/main.py
