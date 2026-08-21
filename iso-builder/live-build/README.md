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
- `common/hooks/live/` - chroot hooks (account creation, etc).
- `amd64/`, `i386/` - one profile per architecture. Each `auto/config`
  script symlinks `config/package-lists`, `config/hooks`, and
  `config/includes.chroot` back to `common/` and the repo-root
  `overlays/` directory at config-time, so those stay the single
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
  than a separate, unmanaged default account (historically named
  "user"). Sourced from `live-config(7)`, not yet build-tested against
  a real boot. Whether live-config also needs to be told explicitly to
  stand down (vs. just aligning its target username) is an open
  question for Phase 3, which owns the adjacent live-boot
  boot-parameter surface for OverlayFS immutability - see the account
  hook's own comments.
