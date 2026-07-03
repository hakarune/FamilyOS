# FamilyOS

An intentionally lightweight, systemd-free, custom Linux distribution built on top of **Devuan GNU/Linux**, engineered to be compatable with older hardware and family-focused environments.

FamilyOS is designed to revive aging machines, strip out corporate telemetry and unnecessary background plumbing, and provide a secure, predictable, and low-maintenance digital sandbox for children and families.

---

## Project Core Pillars

1. **Systemd-Free Architecture**  
   Built natively on **Devuan**. Utilizing lightweight, deterministic init systems (`sysvinit` / `openrc`) to eliminate modern service bloat, reduce attack vectors, and ensure blindingly fast boots on legacy spinning disks.
   
2. **Aggressive Resource Optimization**  
   Targeting older desktop and laptop hardware. Memory consumption at idle is restricted to absolute minimum thresholds by using an ultra-light window manager setup instead of a heavy desktop environment.

3. **Digital Privacy & Sovereignty**  
   Zero diagnostic telemetry, zero forced background connections, and out-of-the-box local network protection.

4. **Resilient Family Sandbox**  
   Immutable baseline filesystems, easily manageable user space permissions, and automated kiosk/restricted-session boundaries to ensure the OS cannot be accidentally bricked by unprivileged users.

---

## Technical Architecture

| Component | Choice | Rationale |
| :--- | :--- | :--- |
| **Upstream Base** | Devuan Stable | Solid Debian core reliability without the systemd pid1/journald footprint. |
| **Init System** | `sysvinit` + `inittab` | Predictable, lightweight, shell-script driven initialization process. |
| **Window Manager** | Ultra-light WM (TBD) | Maximizes video memory and CPU cycles for user-space applications. |
| **Package Manager**| `apt` + `dpkg` | Native Debian package ecosystem with custom local repositories. |
| **File Systems**   | `ext4` or `Btrfs` | Balance of legacy reliability and modern snapshot capabilities. |

---

## Repository Roadmap & Structure

```text
familyos-core/
├── build-scripts/      # Staging, debootstrap, and live-sdk build orchestrators
├── config/             # System configuration overlays (/etc, skeleton profiles)
├── packages/           # Custom meta-packages, pins, and custom repository manifests
├── artwork/            # Branding, custom plymouth themes, and default wallpapers
└── README.md           # This file

```

### Current Milestone: Phase 1 — Automated Image Bootstrapping

* [ ] Architect baseline `debootstrap` configuration scripts for staging the Devuan core.
* [ ] Configure custom APT pinning to strictly reject systemd dependencies (`libsystemd0` minimization).
* [ ] Implement localized user profiling and default permission skeletons (`/etc/skel`).
* [ ] Establish an isolated build container environment to cleanly generate the bootable live ISO images.

---

## Building & Contributing

*(Detailed instructions for staging the live ISO compiler will be documented here once the bootstrap scripts are committed.)*

### Prerequisites

To build the distribution image from source, you will need a clean Debian/Devuan build environment with the following dependencies staged:

* `debootstrap`
* `live-build` / `xorriso`
* `squashfs-tools`

---

## 📄 License

This project is open-source software licensed under the GPL-v3. See the `LICENSE` file for full terms and conditions.
