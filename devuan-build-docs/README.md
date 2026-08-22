
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
