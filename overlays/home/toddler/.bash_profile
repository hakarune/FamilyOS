# Starts the FamilyOS kiosk session on TTY1 login. See .xinitrc for
# what actually gets launched, and overlays/etc/inittab for the
# passwordless autologin that reaches this login shell in the first
# place.
#
# stdout/stderr from the X session are captured to a log file so a
# crash after Openbox/the launcher have already started (which won't
# necessarily trip sysvinit's respawn-too-fast protection - see
# iso-builder/live-build/README.md) is at least diagnosable from TTY2
# afterward, instead of silently lost.
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    exec startx > "$HOME/.familyos-xsession.log" 2>&1
fi
