# FamilyOS Master Development Roadmap

This chronological roadmap dictates project milestones. AI workspace tools should consume this sequence to generate codebases incrementally.

**Status: all four phases below are complete.** The first successful CI build
produced a real, successfully-built FamilyOS `amd64` ISO via
`iso-builder/live-sdk/` (see "Live-build → live-sdk rebase" below) - CI
verifies the build completes and boot-critical files land as real files,
not that the image actually boots; see `Readme.md`'s "What's next" for
that gap and the current top-level project status.

## Phase 1: Repository & Tool Scaffolding
- [x] Initialize git repository with the structure defined in `Github Project Structure.md`.
- [x] Generate the custom `FamilyOS Launcher` Python/PyQt code base based on `Flavor - Toddler.md`.
- [x] Draft the `familyos-cli` parental control script for TTY2 management.

## Phase 2: Live Build Infrastructure
- [x] Configure the Devuan minimal live-build environment profiles for `amd64` and `i386`.
- [x] Write configuration files to enforce passwordless auto-login to TTY1 for the `toddler` user.
- [x] Script the Openbox `rc.xml` configuration overlay to strip all default windows management controls.

*(Originally built on live-build; see the rebase note below. `i386` has a
config profile in both tools but has never actually been built/tested -
`amd64` is the only architecture a real build has been run for.)*

## Phase 3: System Hardening
- [x] Implement the `OverlayFS` immutable boot parameters in the live image.
- [x] Build the network-filtering scripts and hardcoded DNS parameters.
- [x] Integrate Kiosk configurations for the designated Web Browser engine.

*(Originally built on live-build; see the rebase note below. The kiosk
browser ended up as a custom embedded `QWebEngineView`
(`launcher/browser_kiosk.py`), not the Min Browser `Browser.md` originally
named - see that file's own note and `launcher/README.md`'s "Tech
decisions" for why.)*

## Phase 4: Branding & ISO Mastering
- [x] Inject custom SVG layouts, splash sheets, and icon packs.
- [x] Run test builds generating raw `.iso` targets.

*(First real `.iso` was produced by a GitHub Actions CI run building with
`iso-builder/live-sdk/`, not the originally-planned `live-build` - see
below. That first artifact had a wrong-codename filename and a few
packaging/warning issues, since fixed - see `devuan-build-docs/` and this
repo's commit history for the follow-up fixes.)*

## Live-build → live-sdk rebase

Phases 2 and 3 were originally implemented entirely on Debian/Devuan
`live-build` (`iso-builder/live-build/`). That tooling kept surfacing
Ubuntu-vs-Devuan internal default mismatches when run in CI (kernel package
naming, `casper` vs `live-boot`, mirror selection) - all traced to one root
cause, live-build's `LB_MODE` auto-detecting from the CI runner's own host
OS rather than the `--distribution` target (see
`devuan-build-docs/confirmed-live-build-package.txt`). Rather than keep
patching around a host-OS-detection bug in vendored tooling, the project
switched to `live-sdk`/`libdevuansdk` - Devuan's own real live-ISO build
tooling, confirmed directly against Devuan's actual release archive to be
what builds the real daedalus ISOs (see
`devuan-build-docs/confirmed-live-sdk.txt`). Phases 2 and 3's requirements
were rebuilt on `live-sdk` rather than re-derived from scratch: the
requirement (auto-login, Openbox lockdown, OverlayFS boot params, DNS/net
filtering, kiosk browser) didn't change, only which build tool assembles
it. `iso-builder/live-build/` is kept as a superseded fallback, not
deleted - see that directory's own README.
