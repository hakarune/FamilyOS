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
   toddler may run these specific binaries, not *who* is asking. Both
   callers (`../launcher/ui/parent_panel.py` and `familyos-cli`) must
   actually invoke `sudo /usr/local/bin/familyos-<script>` (the exact
   path this sudoers rule whitelists) to get here - **a real QEMU boot
   test found both callers were invoking the scripts directly instead,
   with no `sudo` at all**, so every privileged action (reboot,
   shutdown, net-toggle, volume) silently ran as the unprivileged
   `toddler` user and failed. Fixed in both.
3. Each privileged script then re-checks identity itself, now running
   as root: it reads a password from stdin (piped by the caller, never
   passed via argv or an env var, so it never shows up in `ps`) and
   verifies it against the `parent` account through the
   `familyos-parent` PAM service
   (`overlays/etc/pam.d/familyos-parent`), via the shared
   `lib/require-parent-auth.sh` helper. **This is the actual gate.**
   `familyos-verify-auth` runs just this check with no side effects,
   for the launcher's "Unlock" step (see `../launcher/ui/parent_panel.py`) -
   this is a UI-side convenience gate so action buttons stay disabled
   until a password actually verifies, not a replacement for this one.
4. `lib/env-guard.sh` makes real system-changing commands (reboot,
   volume, network rules) print `[DRY RUN] would execute: ...` instead
   of running, unless `/etc/familyos-release` exists - **a real QEMU
   boot test confirmed this marker file was never created by either
   build tool, so every script here always ran in dry-run mode even on
   the real CI-built ISO. Fixed:** both `familyos.blend`'s finalize
   script and the live-build `0020-register-init-scripts.hook.chroot`
   equivalent now write it during the image build.

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
| `familyos-remount-rw` | implemented (dry-run guarded) | Ownership-gated copy into `/home/toddler/media`, not a literal mount remount - see the script's own header comment for why. Needs the persistence partition described in `iso-builder/live-build/persistence-media/README.md` to survive reboot; degrades safely without it. The directory's `parent:toddler 750` ownership is reasserted every boot by `familyos-media-perms` (`overlays/etc/init.d/`), since live-boot's persistence union mount does not reliably preserve the build-time ownership - see that script's own header comment. |
| `familyos-cli` | implemented | whiptail menu wrapping the scripts above |
| `familyos-verify-auth` | implemented | no-op auth check for the launcher's "Unlock" step - see "Auth & privilege contract" above |
| `familyos-sites` | implemented | `list`/`add <name> <url>`/`remove <host>` for `/var/lib/familyos/allowed-sites.json`, the parent-curated site list `../launcher/browser_kiosk.py`'s homepage and navigation allowlist are both generated from - see `lib/sites-edit.py` (validation, JSON edit) and `lib/render-homepage.py` (regenerates the local homepage after every change). Needs the persistence partition (same as `familyos-remount-rw` below) to survive reboot; degrades safely to the build-time default (KidzSearch + BRAVE+) without it. |
| `lib/net-rules.sh` | implemented | shared `apply_net_state on\|off`, used by both `familyos-net-toggle` and the boot-time `familyos-net-lock` init script |

## Known open items

- `pamtester` is confirmed available and installed in the real CI-built
  image (`devuan-build-docs/confirmed-package-sweep.txt`,
  `build.log`). Still not independently confirmed: that the
  `familyos-parent` PAM service config is complete and actually accepts
  a correct `parent` password / rejects an incorrect one end-to-end -
  the first real boot test didn't reach this check (blocked by the
  sudo-invocation and path bugs above) - verify on the next boot test
  now that both are fixed.
- `iptables-restore`'s full-table-replace behavior (no `--noflush`) in
  `lib/net-rules.sh` is documented/well-understood, but the specific
  rule set has not been applied against real hardware/network
  interfaces - verify on first real build.
- The DoH mitigation in `browser_kiosk.py`
  (`QTWEBENGINE_CHROMIUM_FLAGS="--disable-features=DnsOverHttpsUpgrade"`)
  targets the correct Chromium base::Feature and is architecturally
  sound (QtWebEngine embeds Chromium's content/net layers, not the
  chrome/browser layer that owns the pref-driven explicit DoH mode a
  full browser exposes - the automatic-upgrade path this flag gates is
  the only way DoH could activate in an app with no settings UI at
  all) - but this reasoning has not been confirmed by running the
  actual built image. Smoke-test before shipping. `lib/net-rules.sh`'s
  DoH-resolver IP blocklist is defense-in-depth underneath this, not a
  substitute, and is not exhaustive.
- `familyos-remount-rw`'s persistence (and, as of this round,
  `familyos-sites`'s allowed-sites list too) depends on a partition that
  doesn't exist until someone masters the boot medium per
  `iso-builder/live-build/persistence-media/README.md` (a post-build
  deployment step, not part of the four development phases - it hasn't
  been re-derived for `live-sdk` specifically, but the mechanism is
  boot-medium-side and tool-agnostic) - without it, both still work but
  only for the current boot session.
- BRAVE+ (`watch.braveplus.com`, one of the two default seeded sites in
  `familyos-sites`) requires a paid account login, and its actual video
  CDN domain(s) beyond the one confirmed (`alpha.uscreencdn.com`)
  weren't fully enumerable without a live, authenticated playback
  session. KidzTube's YouTube-embedded videos may also carry a clickable
  "Watch on YouTube" escape link out of the embedded player - not
  confirmed either way. Both need a real login/playback test - see
  `devuan-build-docs/confirmed-browser-homepage-domains.txt` for the
  full research trail and exactly what to check.
