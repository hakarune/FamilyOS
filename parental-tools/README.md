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
   volume, network rules) print `[DRY RUN] would execute: ...` instead
   of running, unless `/etc/familyos-release` exists - a marker file
   that won't be authored until Phase 2/4, so every script here is safe
   to run on a developer's own machine today.

## Exit code contract

- `0` - succeeded.
- `1` - failed (including failed auth).
- `2` - not implemented yet (the caller should show "coming in a later
  phase," not report success or a generic error). Nothing currently in
  this directory uses this code - every script is now implemented -
  but the contract is kept for any future addition.

## Scripts

| Script | Status | Notes |
| --- | --- | --- |
| `familyos-power` | implemented (dry-run guarded) | reboot/poweroff |
| `familyos-volume` | implemented (dry-run guarded) | `Audio Architecture.md` |
| `familyos-net-toggle` | implemented (dry-run guarded) | `on`/`off` - see `lib/net-rules.sh`. Only lasts the current boot - `familyos-net-lock` re-applies the OFF baseline every boot. |
| `familyos-remount-rw` | implemented (dry-run guarded) | Ownership-gated copy into `/home/toddler/media`, not a literal mount remount - see the script's own header comment for why. Needs the persistence partition described in `iso-builder/live-build/persistence-media/README.md` to survive reboot; degrades safely without it. |
| `familyos-cli` | implemented | whiptail menu wrapping the scripts above |
| `lib/net-rules.sh` | implemented | shared `apply_net_state on\|off`, used by both `familyos-net-toggle` and the boot-time `familyos-net-lock` init script |

## Known open items

- Confirm `pamtester` is actually available in Devuan's repos (assumed
  here, not verified - this dev environment has no PAM stack to test
  against).
- Confirm the `familyos-parent` PAM service config is complete once
  tested against a real Devuan target - it currently only has `auth`
  and `account` lines.
- `iptables-restore`'s full-table-replace behavior (no `--noflush`) in
  `lib/net-rules.sh` is documented/well-understood, but the specific
  rule set has not been applied against real hardware/network
  interfaces - verify on first real build.
- The DoH mitigation in `browser_kiosk.py`
  (`QTWEBENGINE_CHROMIUM_FLAGS="--disable-features=DnsOverHttps"`) uses
  a confirmed env-var mechanism but an unverified exact Chromium
  feature-flag string - smoke-test against the actual built image.
  `lib/net-rules.sh`'s DoH-resolver IP blocklist is defense-in-depth
  underneath this, not a substitute, and is not exhaustive.
- `familyos-remount-rw`'s persistence depends on a partition that
  doesn't exist until someone masters the boot medium per
  `iso-builder/live-build/persistence-media/README.md` (Phase 4
  territory) - without it, the tool still works but only for the
  current boot session.
