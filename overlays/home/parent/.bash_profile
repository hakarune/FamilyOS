# Runs the FamilyOS parent CLI automatically after a normal login on
# this account (TTY2 - see overlays/etc/issue). This is a convenience
# wrapper, not the auth boundary: familyos-cli's own privileged actions
# are still gated by the real PAM check inside parental-tools' scripts
# (see ../../../parental-tools/README.md). Logging into this account at
# all already requires a real Devuan password (set via a Phase 3/4
# first-boot flow - see the account-creation hook's comments), so this
# is a second, complementary layer, not a bypass.
if [ "$(tty)" = "/dev/tty2" ]; then
    exec /usr/local/bin/familyos-cli
fi
