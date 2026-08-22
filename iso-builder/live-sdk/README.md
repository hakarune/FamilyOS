# FamilyOS on live-sdk

Replaces `iso-builder/live-build/` (see that directory's own README for the
tool being replaced and why). This directory holds FamilyOS's blend for
[live-sdk](https://github.com/devuan/live-sdk) + its
[libdevuansdk](https://github.com/devuan/libdevuansdk) dependency - Devuan's
own live-ISO build tooling, confirmed directly against Devuan's real release
archive (`files.devuan.org/devuan_daedalus/desktop-live/README_desktop-live.txt`:
"Built with the Devuan SDK, live-sdk module by jaromil and parazyd").

Full research trail, including what was and wasn't possible to verify
without a real build: `devuan-build-docs/confirmed-live-sdk.txt`.

## Layout

```
iso-builder/live-sdk/
└── blends/
    └── familyos/
        ├── config              # arch, release, mirror, FamilyOS package list
        ├── familyos.blend      # blend_preinst/blend_postinst, isolinux override
        └── daedalus/
            └── isolinux_overlay/
                └── isolinux.cfg  # boot menu + kernel command line
```

`live-sdk` and `libdevuansdk` themselves are NOT vendored into this repo -
CI installs them fresh from Devuan's own git hosting on every run (see
`.github/workflows/build-iso.yml`), the same "install the real Devuan tool,
don't assume the CI runner's own package manager has it" pattern already
used for `debootstrap`.

`daedalus/rootfs_overlay/` does not exist as a committed directory - it's
never created at all. Unlike the reference blends bundled with upstream
live-sdk (which commit a static `rootfs_overlay/` tree), FamilyOS's
`familyos.blend` copies `overlays/etc`, `overlays/home`, `parental-tools/`,
`launcher/`, and `graphics/` directly from the repo root at build time
(inside `blend_postinst`), the same "single source of truth, materialized
at build time" approach `iso-builder/live-build/{amd64,i386}/auto/config`
already used. There is exactly one copy of e.g.
`overlays/home/toddler/.config/openbox/rc.xml` to maintain, not two.

## Invoking a build

live-sdk is normally used interactively (`zsh -f -c 'source sdk'`, then type
`load ...` and `build_iso_dist` by hand at a prompt), but every function in
its build path is plain, non-interactive zsh - confirmed by tracing
`build_iso_dist()`'s full call graph for `read`/`vared`/`select`/TTY
dependencies (see `devuan-build-docs/confirmed-live-sdk.txt`). CI invokes it
as one non-interactive command:

```sh
ARCH=amd64 FAMILYOS_REPO_ROOT=/path/to/this/repo zsh -f -c '
    source sdk
    os="devuan"
    arch="${ARCH:-amd64}"
    oslib="$R/lib/libdevuansdk/libdevuansdk"
    source "$oslib"
    blendlib="$R/blends/familyos/familyos.blend"
    source "$blendlib"
    export BLEND=1
    workdir="$R/tmp/${os}-${arch}-build"
    strapdir="$workdir/bootstrap"
    mkdir -p "$strapdir"
    export LANG=C
    export LC_ALL=C
    source "$R/lib/zuper/zuper.init"
    build_iso_dist
'
```

(run from live-sdk's own cloned root, with this blend's directory copied to
`blends/familyos` inside it - see the CI workflow for the exact setup
steps. `FAMILYOS_REPO_ROOT` must point at this repo's checkout -
`familyos.blend` cannot derive it from its own location, since it no
longer lives at a fixed relative depth under this repo once copied into
live-sdk's own directory tree.)

This is deliberately NOT `load devuan familyos daedalus`. live-sdk's own
`load()` (in the `sdk` file) looks blend names up in a `blend_map` array
hardcoded inside that function's body (`devuan-desktop-live`,
`devuan-minimal-live`, `heads`, `decode`) - `familyos` can't be added to it
without patching live-sdk's own vendored file, and an unregistered name is
a soft failure (`act "No blend specified"`, not `die`) - the exact same
silent no-blend-loaded trap live-sdk's own README quickstart example falls
into with `load devuan amd64`. (An independent critique pass caught this in
the first draft of this build - see `devuan-build-docs/confirmed-live-sdk.txt`.)
The snippet above replicates `load()`'s actual work directly against this
blend's own known path instead of going through that lookup, without
patching any vendored live-sdk file.

## What's a deliberate deviation from upstream's example blends

- `arch="${ARCH:-amd64}"` in `config`, instead of a hardcoded `arch="amd64"`
  a human is expected to hand-edit before each build - lets one blend
  directory serve both amd64 and i386 from CI.
- `linux-image-686-pae` for i386, not `linux-image-686` (live-sdk's own
  bundled example config uses the latter - the non-PAE flavour Debian/Devuan
  dropped after stretch; see `devuan-build-docs/confirmed-kernel-packages.txt`).
- Two locked, passwordless accounts (`toddler`, `parent`) created in
  `blend_preinst`, not the reference blends' single `username`/`userpass`
  model.

## Known unresolved gap

Devuan's real daedalus-era blend definitions (the ones that actually built
the ISOs at files.devuan.org) were not found published anywhere reachable
during this rebase - not in the GitHub mirrors this blend is modeled on,
not in fsmithred's public blend tarball drops (stop at beowulf/2020), and
`git.devuan.org` (named in a forum post as the canonical host) is behind a
proof-of-work anti-bot challenge that couldn't be solved without a real
browser. This blend was written from FamilyOS's own already-correct
`overlays/`/`parental-tools/`/`launcher/` content plus the *structural*
conventions of the stale (beowulf-era) example blends - not validated
against any working daedalus reference. See
`devuan-build-docs/confirmed-live-sdk.txt` for the full trail. If you can
reach `git.devuan.org/devuan-sdk/live-sdk` from a real browser, checking it
for a newer blend or core update would be worth doing before relying on
this in production.
