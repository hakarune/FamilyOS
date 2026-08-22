# iso-builder/live-build

**SUPERSEDED, kept as a fallback, not deleted.** CI
(`.github/workflows/build-iso.yml`) now builds FamilyOS with
`iso-builder/live-sdk/` instead - Devuan's own build tooling, replacing
live-build after live-build kept surfacing Ubuntu-vs-Devuan internal
default mismatches (kernel package naming, casper vs live-boot, mirror
selection - all traced to one root cause, `LB_MODE` auto-detecting from
the CI runner's own OS; see `devuan-build-docs/confirmed-live-build-package.txt`).
See `iso-builder/live-sdk/README.md` for the replacement and
`devuan-build-docs/confirmed-live-sdk.txt` for the full research trail.

This directory is deliberately still here rather than deleted: the
live-sdk rebase has not yet had a real CI run (this authoring
environment cannot execute either build tool - see below), so there is
currently no build that has actually been proven to work end-to-end.
Once a real `live-sdk` CI run succeeds, this directory should be
removed - ask before deleting it before that point.

Live-build (`lb`) profiles for FamilyOS, one per target architecture
per `_Base Architecture Overview.md`'s "Target Architectures" list.
These profiles have **not** been build-tested locally: this repo was
authored in an environment with no working `live-build` chroot tooling
(Android/Termux - proot's ptrace-based syscall emulation breaks
debootstrap's device-node creation). Real build validation happens via
GitHub Actions instead - see "CI build validation" below.

## Layout

- `common/package-lists/familyos.list.chroot` - shared package list.
- `common/hooks/live/` - chroot hooks: account + persistent-media-dir
  creation, init-script registration (`familyos-dns-lock`,
  `familyos-net-lock`, `familyos-media-perms`), parental-tools
  installation, optional Plymouth install (see below).
- `persistence-media/` - the `persistence.conf` template for the
  optional persistent media partition, and instructions for actually
  creating that partition (Phase 4/deployment work, not something a
  chroot build can do).
- `amd64/`, `i386/` - one profile per architecture. Each `auto/config`
  script builds `config/includes.chroot` as a real directory populated
  with **dereferencing copies** (`cp -rL`, not symlinks) of `overlays/`
  (per top-level entry), `parental-tools/` → `/usr/local/lib/familyos/`,
  `launcher/` → `/opt/familyos/`, `graphics/` → `/opt/familyos/graphics`,
  and `graphics/splash/` → `/usr/share/plymouth/themes/familyos`. Copies
  rather than symlinks specifically because live-build's handling of
  symlinks placed inside `includes.chroot` is undocumented and
  unverified here - a naive preserve-the-symlink copy would ship
  dangling symlinks pointing at a build-host path, silently breaking
  the boot chain. `config/package-lists` / `config/hooks` are still
  symlinked back to `common/` (those are live-build's own build-host
  config, never copied into the target image, so the risk doesn't
  apply). Nothing here is committed as repo symlinks regardless - the
  authoring environment's storage backend doesn't support them.

## Building (untested locally - see CI below)

    cd amd64   # or i386
    lb config
    lb build

## CI build validation

`.github/workflows/build-iso.yml` runs `lb config && lb build` for the
amd64 profile on `ubuntu-latest` (real root, real loop mounts - not
subject to the local proot limitations above), then verifies real
files (not dangling symlinks) exist at the critical install paths
before uploading the result. This is the actual Step 5 (`Development
Roadmap.md` Phase 4) validation mechanism - check the repo's Actions
tab for run results; this authoring environment has no authenticated
`gh` session to trigger or monitor it directly.

## Known open items / unverified assumptions

- **Kernel flavour:** i386 uses the `686-pae` flavour
  (`linux-image-686-pae` metapackage, not a hardcoded ABI-versioned
  package name). This is the *only* currently-packaged i386 kernel
  flavour in Debian/Devuan (non-PAE was dropped after stretch) - if any
  specific target Eee PC board lacks PAE support, i386 is not viable on
  that board regardless of packaging choices. Confirm against the real
  target hardware list during Phase 4 validation. If `_Base Architecture
  Overview.md`'s "686-rt" reference turns out to mean the
  realtime-preempt flavour rather than shorthand for 686-pae, the
  candidate package is `linux-image-rt-686-pae` - not yet confirmed to
  exist in Devuan's `daedalus` archive.
- **`live-config-systemd-` exclusion syntax:** the trailing-dash
  removal marker is confirmed APT syntax, but not confirmed to be
  honored by live-build's own `package-lists/*.list.chroot` parser
  (which does its own line handling before invoking apt). If `lb build`
  errors on that line, fall back to an APT pinning file at
  `config/archives/familyos.pref` instead (the live-manual's documented
  package-exclusion mechanism).
- **`--initsystem sysvinit` alone** has a documented history (Debian
  bug #772651) of not reliably keeping `live-config-systemd` out of the
  package set, which is why `familyos.list.chroot` also explicitly
  requests `live-config-sysvinit` and excludes `live-config-systemd`.
- **`live-config.username=toddler`** is passed via `--bootappend-live`
  so that IF live-config's own boot-time autologin logic runs, it
  targets the same `toddler` account the chroot hook creates rather
  than a separate, unmanaged default account. Sourced from
  `live-config(7)`, not yet build-tested against a real boot.
- **`persistence persistence-label=familyos-data`:** enables live-boot's
  persistence mechanism, pinned to a specific partition label so an
  unrelated stray persistence-labeled partition on the same medium is
  never accidentally honored. Confirmed: live-boot only probes for
  persistence media when the `persistence` parameter is present at all
  (so its prior omission was already safe) - not yet confirmed:
  whether `persistence.conf`'s custom-mount line syntax (see
  `persistence-media/persistence.conf`) is exactly right; needs a real
  boot test. Confirmed (Phase 3 audit): live-boot's `persistence.conf(5)`
  explicitly skips its "optimistic" ownership-from-source-directory
  propagation for `union`-option entries like this one, and the merged
  directory's ownership instead comes from live-boot's own `mkdir` on
  the persistent partition - so the account hook's build-time
  `parent:toddler 750` on `/home/toddler/media` does not reliably
  survive once persistence is active. Fixed via a dedicated boot-time
  init script, `familyos-media-perms`, that reasserts it every boot
  regardless of mount state - see `parental-tools/README.md`.
- **DNS lockdown is boot-script-based, not build-time.** The
  build-time `chattr +i` attempt in
  `common/hooks/live/0020-register-init-scripts.hook.chroot` is very
  likely a no-op - the immutable inode flag almost certainly has no
  slot in squashfs's on-disk format, and OverlayFS copy-up does not
  reliably propagate it either. The real mechanism is
  `overlays/etc/init.d/familyos-dns-lock`, which writes DNS content
  directly into the live tmpfs layer and chattrs that copy instead -
  tmpfs's own support for the immutable flag via `FS_IOC_SETFLAGS` was
  confirmed present (and bugfixed) before Linux 6.0 final, and Devuan
  `daedalus` ships 6.1 LTS, so this should genuinely work. dhclient is
  separately prevented from ever overwriting resolv.conf (including on
  lease renewal) via
  `overlays/etc/dhcp/dhclient-enter-hooks.d/familyos-dns-lock`.
- **Network fail-safe default:** `familyos-net-lock` applies the
  internet-OFF baseline on every boot, unconditionally - a deliberate
  value judgment (a hard power-cycle is always possible and outside
  software's control, so landing in "no WAN" after any reboot is safer
  than "whatever the last session had"), not just an implementation
  detail. See `parental-tools/README.md`.
- **Browser:** built as a custom embedded `QWebEngineView`
  (`launcher/browser_kiosk.py`), not a standalone browser app - neither
  Min (no i386 build since Electron dropped 32-bit Linux support, and
  its Focus Mode doesn't actually restrict the URL bar) nor Falkon (no
  native lockdown mode beyond a `--fullscreen` toggle) can deliver what
  `Browser.md` describes. `python3-pyqt5.qtwebengine` is confirmed
  present in Debian's archives across amd64/i386/arm64/armhf.
- **Plymouth boot splash is best-effort, not guaranteed.** Installed
  via `common/hooks/live/0040-optional-plymouth.hook.chroot`, isolated
  from the main package list specifically so a failure there can't
  fail the whole build. Debian's stock `plymouth` package depends on
  `systemd (>=232-8) | elogind` and `udev (>=232-8)`; `elogind` and
  Devuan's `eudev` (Provides: udev) should satisfy both via the
  non-systemd alternative, matching how this project already handles
  `live-config-sysvinit` elsewhere - but whether that `systemd |
  elogind` alternative actually made it into the plymouth version
  daedalus ships is unconfirmed (the Debian fix landed in testing
  2023-12-16, after both bookworm's freeze and daedalus's release).
  Check the CI build log's `0040-optional-plymouth` hook output to see
  which way it went on a real build. If it failed, do not reach for
  the JoeThunder out-of-tree patch - unmerged/experimental, not
  reliable enough for this project. A plain text boot without a splash
  is the correct fallback.
- **Icon/asset sourcing:** see `docs/Asset_Sourcing.md` and
  `graphics/ASSET_INVENTORY.md` for the full asset-by-asset record,
  including the finding that sugar-artwork has no usable matches for
  any current app-grid icon (all four are Papirus fallbacks in
  practice, not sugar-artwork originals).
