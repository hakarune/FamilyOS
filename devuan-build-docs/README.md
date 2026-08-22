
## Regenerating package indexes

confirmed-kernel-packages.txt and confirmed-familyos-packages.txt were both
extracted from Devuan's full daedalus package indexes:
- http://deb.devuan.org/merged/dists/daedalus/main/binary-amd64/Packages.gz
- http://deb.devuan.org/merged/dists/daedalus/main/binary-i386/Packages.gz

These are ~50MB uncompressed and were deleted after extracting the relevant
entries. Re-download and grep again if other package names need verification.
Extraction note: a real Packages index has multi-field, blank-line-delimited
stanzas (not the short kernel-only ones), so a plain `grep -A6` misses fields;
use paragraph-mode awk that splits each record on "\n" and matches the first
line exactly against "Package: <name>" instead of relying on regex `^`/`$`
matching mid-record (gawk's paragraph mode does NOT do that by default).

confirmed-debootstrap-scripts.txt was produced by taking the `debootstrap`
package's `Filename:`/`SHA256:` fields straight out of the binary-amd64 index
above, downloading that exact `.deb` from
http://deb.devuan.org/merged/<Filename>, verifying its SHA256 against the
index, then listing its contents with `dpkg-deb -c` and grepping
`usr/share/debootstrap/scripts/` - this is what actually confirms the
`daedalus -> ceres` symlink claim; the Packages.gz stanza alone is metadata
only and can't prove a file-listing claim like that.

confirmed-live-build-package.txt was produced the same way, but for the
`live-build` package: downloaded the exact `.deb` from its Filename/SHA256
fields, verified the checksum, extracted with `dpkg-deb -x`, then grepped
`usr/share/live/build/functions/defaults.sh` for its `LB_MODE`
auto-detection and every `case "${LB_MODE}"` branch it drives - this is what
confirms LB_MODE (auto-detected from the build host's `lsb_release`, not the
`--distribution` target) is the actual root cause behind the mirror,
kernel-package, and casper-vs-live-boot fixes, not three unrelated bugs.

confirmed-live-sdk.txt documents the full-rebase decision from live-build to
live-sdk (Devuan's own build tooling, see iso-builder/live-sdk/README.md):
confirmed directly against Devuan's real release archive
(files.devuan.org/devuan_daedalus/desktop-live/README_desktop-live.txt) that
live-sdk built the actual daedalus ISOs, confirmed by tracing
libdevuansdk's real source (cloned from github.com/devuan/{live-sdk,
libdevuansdk}) that its build pipeline runs fully non-interactively and has
no LB_MODE-equivalent host-OS auto-detection bug class, and documents one
unresolved gap: the real daedalus-era blend sources were not found
published anywhere reachable (git.devuan.org, named as the canonical host,
is behind an unsolvable-without-a-browser anti-bot challenge).

confirmed-package-sweep.txt documents a full sweep of every package name
the live-sdk build chain actually installs (libdevuansdk's own
core_packages/base_packages, live-sdk's own extra_packages baseline, and
this blend's own additions), triggered by a real CI failure
("Package btrfs-tools is not available"). Checked each one against a real
download of daedalus's main/contrib/non-free indexes: found and fixed
three obsolete/nonexistent vendor-default package names (btrfs-tools,
git-core, firmware-linux) and one wrong-kernel-flavour duplicate
(linux-image-686 alongside linux-image-686-pae on i386), all excluded or
renamed blend-side via zsh's `${array:#pattern}` syntax rather than by
patching either vendored config file. Also confirms no package in the
chain has a hard (Depends:, not Recommends:) dependency on systemd.
