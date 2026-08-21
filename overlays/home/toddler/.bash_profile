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
    # Dismisses the Plymouth boot splash (if installed - see
    # iso-builder/live-build/common/hooks/live/0040-optional-plymouth.hook.chroot)
    # right as the graphical session takes over. This system has no
    # systemd unit dependency graph to hook plymouth-quit-wait.service
    # into, so a plain command at the point X actually starts is the
    # sysvinit-appropriate equivalent. Silently a no-op if plymouth
    # isn't installed.
    command -v plymouth >/dev/null 2>&1 && plymouth --quit
    exec startx > "$HOME/.familyos-xsession.log" 2>&1
fi
