#!/bin/bash
# Dry-run guard for parental-tools scripts.
#
# FamilyOS identifies a real target system by the presence of
# /etc/familyos-release, an os-release-style marker file expected to be
# authored during Phase 2 (live-build profile) or Phase 4 (branding/ISO
# mastering). Until that file exists - which it never will on a plain
# dev checkout - privileged commands print what they *would* do instead
# of running, so scripts here can be safely executed on a developer's
# own machine.

FAMILYOS_RELEASE_MARKER="/etc/familyos-release"

is_dry_run() {
    [ ! -f "$FAMILYOS_RELEASE_MARKER" ]
}

run_or_dry_run() {
    if is_dry_run; then
        echo "[DRY RUN] would execute: $*"
    else
        "$@"
    fi
}
