# FamilyOS Launcher

Fullscreen kiosk launcher for the Toddler flavor, per
`Project_Vault/Flavor - Toddler.md`. Built with PyQt5 (not PyQt6) - see
"Tech decisions" below.

## Layout

- `main.py` - entry point.
- `ui/main_window.py` - fullscreen borderless app grid.
- `ui/parent_panel.py` - password-gated parent dashboard modal.
- `config/apps.json` - the app catalog rendered as grid buttons.

## Running (dev)

    pip install -r requirements.txt
    python3 main.py

Not runnable/screenshot-tested in this checkout's environment (no X11
display available here) - verified so far only via `python3 -m
py_compile` and manual review.

## Tech decisions

- **PyQt5 over PyQt6:** `Development Roadmap.md`'s Phase 1 line says
  "Python/PyQt," not PyQt6 specifically. PyQt5 has a materially better
  packaging track record on Devuan/Debian i386 (see
  `_Base Architecture Overview.md`'s i386/Atom target), which matters
  more here than being on the latest Qt major version. Open item for
  Phase 2: confirm actual PyQt5 package availability once the
  live-build environment exists.
- **Auth is not implemented in this module.** The parent panel pipes
  the typed password via stdin to scripts in `../parental-tools/`,
  which perform the real PAM-backed check after sudo has already
  elevated them to root. See `../parental-tools/README.md` for the
  full contract.
