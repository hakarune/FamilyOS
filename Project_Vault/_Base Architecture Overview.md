# Base Architecture Overview
 - Base OS: Devuan (`daedalus`)
 - Live system: `live-sdk`/`libdevuansdk` (Devuan's own build tooling; originally
   `live-build`, kept as a superseded fallback - see
   `Development Roadmap.md`'s rebase note and `iso-builder/live-build/README.md`)
 - Desktop: Openbox (XFCE was an original candidate, never implemented)

## Core:
- OverlayFS immutability
- parental controls
- DNS filtering
- hardened browser, with a short, neutral, conservative default web
  allowlist (ad-free or explicitly disclosed where not, no contested
  social/political/religious framing) - a parent-removable floor, not
  a ceiling. See `docs/default-websites.md`.

## Target Architectures
- amd64 (Standard 10-year-old hardware)
- i386 (Legacy Netbooks / Asus Eee PC line - Single-core Atom optimized)

## Kernel Tweak for Legacy:
- Use linux-image-6.1.0-xx-686-pae or 686-rt for low-latency feedback on single-core Atom chips.

## System State & Immutability
- **Root Filesystem:** Read-only via OverlayFS with a `tmpfs` RAM-disk upper layer.
- **Persistence:** Every reboot completely wipes the toddler session changes.
- **DNS Lockdown:** Pre-configured safe DNS written to `/etc/resolv.conf` and locked via `chattr +i`. 

## Display & Login Sequence for Toddler Flavor
1. System boots directly into a Linux text console (no Display Manager like LightDM).
2. `/etc/inittab` or `agetty` triggers an automatic passwordless login for the user `toddler`.
3. The `toddler` user's `~/.xinitrc` starts a bare `Xorg` session launching `openbox` directly.


## Parent Unlock & Administration Flow (Graphical)
Management happens entirely within the graphical environment via a secure, parent-focused overlay to ensure non-technical parents can manage the system without using the command line.

1. **Accessing the Gatekeeper:** The custom Fullscreen Launcher features a secured "Parent Settings" icon.
2. **Authentication:** Clicking the icon triggers a modal overlay requiring parental authentication (Master Password or an interactive parent-verification challenge).
3. **The Parent Dashboard:** Successful authentication reveals a simplified, touch/mouse-friendly management GUI running on top of the Openbox session.
4. **Behind-the-Scenes Execution:** Clicking toggles in this GUI executes backend system scripts safely:
    - **Internet Switch:** Triggers the `net-toggle` script to flush iptables/nftables rules.
    - **Persistent Remount:** For permanent configuration adjustments (like adding a local video file), the GUI temporarily mounts the underlying storage system read-write (`mount -o remount,rw`), writes the change, and immediately locks it back down to read-only.

## Icon & Asset Sourcing
Kid-facing icons (launcher, Toddler flavor UI) and parent-facing icons (Parent Dashboard, settings) come from two different icon sets with two different licenses - **sugar-artwork** (Apache 2.0) for kids, **Papirus** (GPL-3.0) for parents. Full decision record, fallback order, and attribution requirements: see `docs/Asset_Sourcing.md`.