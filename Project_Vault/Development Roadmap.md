# FamilyOS Master Development Roadmap

This chronological roadmap dictates project milestones. AI workspace tools should consume this sequence to generate codebases incrementally.

## Phase 1: Repository & Tool Scaffolding
- [ ] Initialize git repository with the structure defined in `Github Project Structure.md`.
- [ ] Generate the custom `FamilyOS Launcher` Python/PyQt code base based on `Flavor - Toddler.md`.
- [ ] Draft the `familyos-cli` parental control script for TTY2 management.

## Phase 2: Live Build Infrastructure
- [ ] Configure the Devuan minimal live-build environment profiles for `amd64` and `i386`.
- [ ] Write configuration files to enforce passwordless auto-login to TTY1 for the `toddler` user.
- [ ] Script the Openbox `rc.xml` configuration overlay to strip all default windows management controls.

## Phase 3: System Hardening
- [ ] Implement the `OverlayFS` immutable boot parameters in the live image.
- [ ] Build the network-filtering scripts and hardcoded DNS parameters.
- [ ] Integrate Kiosk configurations for the designated Web Browser engine.

## Phase 4: Branding & ISO Mastering
- [ ] Inject custom SVG layouts, splash sheets, and icon packs.
- [ ] Run test builds generating raw `.iso` targets.
