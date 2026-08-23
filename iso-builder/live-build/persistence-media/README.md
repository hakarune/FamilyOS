# iso-builder/live-build/persistence-media

Phase 4 (ISO Mastering)/deployment territory, not something the
live-build chroot profiles in this repo can create themselves: a
physical partition or file is part of the boot medium (USB stick,
internal disk), not the squashfs image these profiles build.

To make `/home/toddler/media` (see `familyos-remount-rw` in
`parental-tools/`) AND `/var/lib/familyos` (the parent-curated
Allowed Websites list + generated browser homepage - see
`parental-tools/familyos-sites` and `launcher/browser_kiosk.py`)
actually survive reboots, whoever masters the final boot medium needs
to:

1. Create a partition (or a loopback file, per live-boot's documented
   persistence mechanisms) labeled exactly `familyos-data` - this
   repo's `auto/config` passes `persistence-label=familyos-data` as a
   boot parameter specifically so ONLY a partition with this exact
   label is ever honored, not an arbitrary stray persistence-labeled
   partition left over from unrelated prior use of the same USB stick.
2. Format it (ext4 recommended) and copy `persistence.conf` (this
   directory) onto it, unmodified.
3. Without this partition present, FamilyOS still boots and runs
   normally - `/home/toddler/media` is just an ordinary empty,
   wiped-every-reboot directory, and `/var/lib/familyos` resets to the
   build-time default site list (KidzSearch, BRAVE+, Starfall,
   Ducksters - see docs/default-websites.md) every boot,
   discarding any parent edits - like everything else. This is a
   degraded-but-safe fallback, not a broken state.

Not build-tested (no live-build/Devuan tooling in this repo's
authoring environment) - the `persistence.conf` line syntax is
believed correct based on published live-boot examples (leading slash,
`union` option) but has not been verified against a real boot.
