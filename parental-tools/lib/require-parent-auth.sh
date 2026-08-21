#!/bin/bash
# Shared privilege gate for FamilyOS parental-tools scripts.
#
# Must be sourced (not executed) by any script that performs a
# privileged action. Reads the parent's password from stdin (piped by
# the caller - familyos-cli or the Qt parent panel - so it never
# appears in argv or the environment, where `ps` could see it) and
# verifies it against the `parent` account via the `familyos-parent`
# PAM service (see overlays/etc/pam.d/familyos-parent).
#
# This check runs *after* sudo has already elevated the caller to root
# (see overlays/etc/sudoers.d/familyos-parent): sudo only decides that
# `toddler` may invoke this specific script, not that the person typing
# is actually a parent. This function makes that second decision.
#
# NOT YET VALIDATED against a real Devuan target/PAM stack - see
# parental-tools/README.md "Known open items."
#
# Exits the calling script with status 1 if authentication fails.

require_parent_auth() {
    local password
    IFS= read -r password

    if ! printf '%s' "$password" | pamtester familyos-parent parent authenticate >/dev/null 2>&1; then
        echo "Authentication failed." >&2
        exit 1
    fi
}
