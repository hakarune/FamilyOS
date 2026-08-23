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

# X's default DPMS/screensaver blanking starts the display blank until
# the first input event wakes it - a real QEMU boot test confirmed
# this as the cause of "boots to a black screen, only renders after
# mouse movement." Disabled outright: a toddler kiosk with no
# unattended-idle privacy concern has no reason to ever blank the
# screen.
xset s off
xset s noblank
xset -dpms

openbox &
exec python3 /opt/familyos/launcher/main.py
