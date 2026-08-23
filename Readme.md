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

- **Boot-test the built ISO** (e.g. in QEMU) - CI currently verifies that
  boot-critical files landed as real files, not that the image actually
  boots to a working Openbox/toddler session.
- **`i386` validation**, if the legacy-netbook target is still wanted -
  the blend config exists but has never been run; see "Architecture
  support" above.
- **Work through the remaining build-log findings** from the AI review of
  the first successful build (`build.log`) - several fixes have already
  landed (ISO codename, Plymouth theme assets, package-name/churn
  cleanup); check `devuan-build-docs/` and recent commit history for
  what's already fixed vs. still open.
- **Smoke-test the kiosk browser's DoH mitigation** and the persistence
  partition workflow against real hardware - both are flagged as
  reasoning-only, not yet build-tested, in `parental-tools/README.md`.
- **Author the `/etc/familyos-release` marker** during the image build -
  nothing currently creates it, so `parental-tools/lib/env-guard.sh`
  still runs every privileged script in dry-run mode even on the real
  CI-built ISO (see `parental-tools/README.md`'s "Known open items").
- **Ongoing content/asset polish** - `graphics/ASSET_INVENTORY.md` and
  `docs/Asset_Sourcing.md` track which icons are still Papirus fallbacks
  rather than sourced from the intended sugar-artwork set.

---

## 📄 License

This project is open-source software licensed under the GPL-v3. See the `LICENSE` file for full terms and conditions.
