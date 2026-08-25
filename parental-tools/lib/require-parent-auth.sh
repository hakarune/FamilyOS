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
# pamtester's actual accept/reject decision against the real
# `familyos-parent` PAM service + a real `/etc/shadow` entry is still
# NOT validated against a real Devuan target - see parental-tools/
# README.md "Known open items". The `read`/EOF bug below WAS confirmed
# by direct reproduction (see its own comment) and blocked reaching
# that pamtester check at all, for any password, on every caller.
#
# Exits the calling script with status 1 if authentication fails.
#
# `read`'s own exit status is deliberately ignored (`|| true`): bash's
# `read` returns non-zero whenever it hits EOF before a delimiter, even
# though it still assigns whatever was read - and every real caller
# pipes the password with no trailing newline (Python's
# `subprocess.run(..., input=password, text=True)` in
# launcher/ui/parent_panel.py's `_unlock`/`_run`/`_sites_command`, and
# `printf '%s' "$password"` in familyos-cli both write the password
# then close stdin, no `\n`). Every script sourcing this runs under
# `set -e`, so without this guard that non-zero `read` status aborted
# the script on the very first line, before the pamtester check ever
# ran - meaning authentication failed unconditionally, for every
# caller, regardless of whether the password was correct. Confirmed by
# reproducing both cases directly: `printf '%s' pw | script` exits 1
# immediately with `read`'s bare exit status; the same input with `||
# true` reaches and correctly evaluates the pamtester check.
# (`familyos-set-password`'s own `new_password` read is unaffected -
# its caller's stdin protocol already ends both lines in `\n`.)

require_parent_auth() {
    local password
    IFS= read -r password || true

    if ! printf '%s' "$password" | pamtester familyos-parent parent authenticate >/dev/null 2>&1; then
        echo "Authentication failed." >&2
        exit 1
    fi
}
