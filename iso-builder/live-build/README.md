# iso-builder/live-build

Live-build (`lb`) profiles for FamilyOS, one per target architecture
per `_Base Architecture Overview.md`'s "Target Architectures" list.
Building an actual `.iso` is Phase 4 (`Development Roadmap.md`) - these
profiles are configuration only, and have **not** been build-tested:
this repo was authored in an environment with no `live-build` package
or Devuan chroot tooling available, so validation here was limited to
structural/syntax review, not an actual `lb build` run.

## Layout

- `common/package-lists/familyos.list.chroot` - shared package list.
- `common/hooks/live/` - chroot hooks: account + persistent-media-dir
  creation, init-script registration (`familyos-dns-lock`,
  `familyos-net-lock`, `familyos-media-perms`), parental-tools
  installation.
- `persistence-media/` - the `persistence.conf` template for the
  optional persistent media partition, and instructions for actually
  creating that partition (Phase 4/deployment work, not something a
  chroot build can do).
- `amd64/`, `i386/` - one profile per architecture. Each `auto/config`
  script builds `config/includes.chroot` as a real directory populated
  with symlinks back to `overlays/` (per top-level entry) plus two
  install-path symlinks (`parental-tools/` → `/usr/local/lib/familyos/`,
  `launcher/` → `/opt/familyos/`), and symlinks `config/package-lists`
  / `config/hooks` back to `common/` - so those all stay the single
  source of truth (per `Github Project Structure.md`) instead of being
  duplicated per architecture. (Not committed as repo symlinks - the
  authoring environment's storage backend doesn't support them.)

## Building (untested - Phase 4 territory)

    cd amd64   # or i386
    lb config
    lb build

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
