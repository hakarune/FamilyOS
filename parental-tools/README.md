# parental-tools

Backend scripts invoked by both the FamilyOS Launcher's parent panel
(`../launcher/ui/parent_panel.py`) and the TTY2 `familyos-cli` menu in
this directory. Both front ends are just UI - all privileged logic and
the actual auth decision live here.

## Auth & privilege contract

1. The launcher runs as the `toddler` user (see
   `_Base Architecture Overview.md`'s auto-login flow), so it cannot
   authenticate as `parent` via `su`/PAM from a GUI process with no
   controlling TTY.
2. Instead, `overlays/etc/sudoers.d/familyos-parent` lets `toddler`
   invoke a fixed, whitelisted set of scripts as root via `sudo`, with
   **no** password prompt at the sudo layer - sudo only decides *that*
   toddler may run these specific binaries, not *who* is asking.
3. Each privileged script then re-checks identity itself, now running
   as root: it reads a password from stdin (piped by the caller, never
   passed via argv or an env var, so it never shows up in `ps`) and
   verifies it against the `parent` account through the
   `familyos-parent` PAM service
   (`overlays/etc/pam.d/familyos-parent`), via the shared
   `lib/require-parent-auth.sh` helper. **This is the actual gate.**
4. `lib/env-guard.sh` makes real system-changing commands (reboot,
   volume) print `[DRY RUN] would execute: ...` instead of running,
   unless `/etc/familyos-release` exists - a marker file that won't be
   authored until Phase 2/4, so every script here is safe to run on a
   developer's own machine today.

## Exit code contract

- `0` - succeeded.
- `1` - failed (including failed auth).
- `2` - not implemented yet (the caller should show "coming in Phase 3",
  not report success or a generic error).

## Scripts

| Script | Status | Depends on |
| --- | --- | --- |
| `familyos-power` | implemented (dry-run guarded) | none |
| `familyos-volume` | implemented (dry-run guarded) | `Audio Architecture.md` |
| `familyos-net-toggle` | stub (exit 2) | Phase 3 - `Internet Toggle with DNS Lockdown.md` |
| `familyos-remount-rw` | stub (exit 2) | Phase 3 - OverlayFS immutability (`Immutability & Parental Control.md`) |
| `familyos-cli` | implemented | whiptail menu wrapping the scripts above |

## Known open items for Phase 2/3

- Confirm `pamtester` is actually available in Devuan's repos (assumed
  here, not verified - this dev environment has no PAM stack to test
  against).
- Confirm the `familyos-parent` PAM service config is complete once
  tested against a real Devuan target - it currently only has `auth`
  and `account` lines.
- Scripts here are invoked by repo-relative path (`../parental-tools/`)
  for Phase 1 dev/testing. `overlays/etc/sudoers.d/familyos-parent`
  assumes the Phase 2/3-installed path `/usr/local/bin/familyos-*`.
  Packaging must reconcile these before Phase 3 ships.
