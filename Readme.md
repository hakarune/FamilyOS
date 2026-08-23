# FamilyOS

An intentionally lightweight, systemd-free, custom Linux distribution built on top of **Devuan GNU/Linux**, engineered to be compatable with older hardware and family-focused environments.

FamilyOS is designed to revive aging machines, strip out corporate telemetry and unnecessary background plumbing, and provide a secure, predictable, and low-maintenance digital sandbox for children and families.

---

## Project Core Pillars

1. **Systemd-Free Architecture**  
   Built natively on **Devuan**. Utilizing `sysvinit` (via `live-config-sysvinit`) to eliminate modern service bloat, reduce attack vectors, and ensure blindingly fast boots on legacy spinning disks.
   
2. **Aggressive Resource Optimization**  
   Targeting older desktop and laptop hardware. Memory consumption at idle is restricted to absolute minimum thresholds by using **Openbox** - an ultra-light window manager - instead of a heavy desktop environment.

3. **Digital Privacy & Sovereignty**  
   Zero diagnostic telemetry, zero forced background connections, and out-of-the-box local network protection (`familyos-net-lock`, `familyos-dns-lock`).

4. **Resilient Family Sandbox**  
   A read-only squashfs root with a `live-boot` OverlayFS/tmpfs upper layer, easily manageable user space permissions, and an automated Openbox kiosk session to ensure the OS cannot be accidentally bricked by unprivileged users.

5. **Neutral, Conservative Default Web Content**  
   The kiosk browser ships with a short, deliberately conservative default site allowlist - ad-free (or explicitly disclosed where not), appropriate for children as young as 5, and free of contested social, political, or religious framing, so a family of any background can boot the image and find the out-of-the-box web content unobjectionable on those grounds. This is a floor, not a ceiling: every default is fully parent-removable, and parents are expected to add their own approved sites via the Parent Panel. See `docs/default-websites.md` for the selection criteria and reasoning.

---

## Technical Architecture

| Component | Choice | Rationale |
| :--- | :--- | :--- |
| **Upstream Base** | Devuan `daedalus` (Devuan 5, bookworm-based) | Solid Debian core reliability without the systemd pid1/journald footprint. |
| **Init System** | `sysvinit` + `live-config-sysvinit` | Predictable, lightweight, shell-script driven initialization process. |
| **Window Manager** | Openbox | Maximizes video memory and CPU cycles for user-space applications. |
| **Package Manager**| `apt` + `dpkg` | Native Debian package ecosystem. |
| **File System**   | squashfs (read-only root) + OverlayFS/tmpfs, `ext4`/FAT for the optional persistence partition | Live-boot's standard immutable-root mechanism; no Btrfs anywhere in this project (persistence is a plain partition, not a snapshotting filesystem). |
| **ISO Build Tooling** | `live-sdk` + `libdevuansdk` (Devuan's own build tooling) | Replaced `live-build` after it kept surfacing Ubuntu-vs-Devuan host-OS default mismatches in CI - see `Project_Vault/Development Roadmap.md`'s rebase note. |

---

## Repository Structure

```text
FamilyOS/
├── iso-builder/            # ISO build tooling: live-sdk/ (current, CI-driven),
│                           # live-build/ (superseded, kept as fallback)
├── overlays/               # Files injected directly into the live ISO root
│   ├── etc/                # Immutable DNS, openbox rc.xml, sudoers.d, init.d
│   └── home/                # toddler/ (kiosk session) and parent/ (admin) homes
├── launcher/               # FamilyOS Launcher - fullscreen kiosk menu (Python/PyQt5)
├── parental-tools/         # Privileged backend scripts + familyos-cli (TTY2)
├── graphics/               # SVGs, Plymouth theme, branding
├── docs/                   # Build/usage documentation, asset sourcing decisions
├── devuan-build-docs/      # Research trail: package/tooling facts verified against
│                           # Devuan's real archives, backing the fixes above
├── Project_Vault/          # Design docs: roadmap, architecture, per-flavor specs
└── Readme.md               # This file
```

## Project Status

**All four planned phases are complete**, and CI has produced a real,
successful `amd64` FamilyOS ISO - built with `iso-builder/live-sdk/`
(Devuan's own build tooling), not the originally-planned `live-build`
(now superseded, kept as a fallback - see
`iso-builder/live-build/README.md`).

- [x] **Phase 1 - Repository & Tool Scaffolding**: launcher, parental-tools,
      and overlay structure in place.
- [x] **Phase 2 - Live Build Infrastructure**: auto-login, Openbox lockdown,
      package profiles - originally on `live-build`, rebuilt on `live-sdk`.
- [x] **Phase 3 - System Hardening**: OverlayFS immutable root, DNS/network
      lockdown, kiosk browser - originally on `live-build`, rebuilt on
      `live-sdk`.
- [x] **Phase 4 - Branding & ISO Mastering**: Plymouth theme, icon/asset
      set, and a real CI-built `.iso` artifact.

Full phase-by-phase detail and the live-build → live-sdk rebase rationale:
`Project_Vault/Development Roadmap.md`.

### Architecture support

CI currently builds and validates **`amd64` only**. An `i386` blend
configuration exists in `iso-builder/live-sdk/` (and the superseded
`iso-builder/live-build/i386/`) as forward-prep for the project's
Eee-PC-class legacy hardware target, but **it has never actually been
built or run** - treat it as untested until a real `i386` CI run succeeds.

---

## Building & Contributing

Real build validation happens via GitHub Actions
(`.github/workflows/build-iso.yml`), which builds the `amd64` ISO on a
real Ubuntu runner (this repo's own authoring environment cannot run
either build tool locally - see `iso-builder/live-sdk/README.md`).

### Prerequisites

To build the distribution image from source, you will need a clean
Debian/Devuan build environment with the following dependencies staged:

* Devuan's `debootstrap` (with the `daedalus` suite script - Ubuntu's
  stock `debootstrap` package doesn't ship it)
* `live-sdk` / `libdevuansdk` (`zsh`) - see `iso-builder/live-sdk/README.md`
* `xorriso`
* `squashfs-tools`

## What's next

With all four planned phases done and a real ISO building in CI, the
remaining work is validation and polish rather than new infrastructure:

- **Re-boot-test the ISO after this round's fixes.** The first real
  QEMU boot test found and this round fixed: the parent-panel privilege
  bugs (wrong script path, missing `sudo`, dry-run always on - see
  `parental-tools/README.md`), the black-screen/DPMS issue, inconsistent
  app fullscreen behavior, no branding/inconsistent button sizing, and
  silent app-launch failures. Confirm all of these actually resolve on
  a fresh build, and specifically confirm the parent panel's real PAM
  auth (correct vs. incorrect password) now that the bugs blocking that
  check from ever running are fixed.
- **`i386` validation**, if the legacy-netbook target is still wanted -
  the blend config exists but has never been run; see "Architecture
  support" above.
- **Plymouth's deeper boot-time failure is still open** - the first
  boot test's "startpar: service(s) returned failure: plymouth" /
  "unexpectedly disconnected from boot status daemon" point at
  plymouthd likely never starting from the initramfs stage, most
  plausibly because plymouth is installed as a late bolt-on rather than
  during normal package staging - not confidently fixable without a
  real boot-log capture. See the display/UX fix commit message and
  `iso-builder/live-build/README.md`'s "Plymouth is best-effort, not
  guaranteed" note.
- **Resolved: the Web Browser is no longer in the toddler grid** -
  moved to a parent-gated "Open Browser" button, with a parent-curated
  homepage replacing the old single hardcoded KidzSearch lockdown. See
  `Browser.md` and `devuan-build-docs/confirmed-browser-homepage-domains.txt`.
- **Smoke-test the kiosk browser's DoH mitigation**, the persistence
  partition workflow, and the new curated-homepage/BRAVE+/KidzTube
  browser work against real hardware - all flagged as reasoning-only or
  partially-confirmed, not yet build-tested, in
  `parental-tools/README.md` and the domains doc above (BRAVE+ login/
  playback, KidzTube's YouTube-embed branding link).
- **Ongoing content/asset polish** - `graphics/ASSET_INVENTORY.md` and
  `docs/Asset_Sourcing.md` track which icons are still Papirus fallbacks
  rather than sourced from the intended sugar-artwork set. Also: the
  Media Player app has nothing to play until a parent actually adds a
  file to `/home/toddler/media` via `familyos-remount-rw` - not a bug,
  but worth a bundled sample/placeholder if a working demo out of the
  box matters.
- **Future ideas logged, not built:** see `docs/future-ideas.md`
  (parent-toggleable app list, multiple interface flavors, a visible
  return-to-launcher affordance over third-party apps).

---

## 📄 License

This project is open-source software licensed under the GPL-v3. See the `LICENSE` file for full terms and conditions.
