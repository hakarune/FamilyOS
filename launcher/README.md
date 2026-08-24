# FamilyOS Launcher

Fullscreen kiosk launcher for the Toddler flavor, per
`Project_Vault/Flavor - Toddler.md`. Built with PyQt5 (not PyQt6) - see
"Tech decisions" below.

## Layout

- `main.py` - entry point.
- `ui/main_window.py` - fullscreen borderless app grid.
- `ui/parent_panel.py` - password-gated parent dashboard modal.
- `config/apps.json` - the static app catalog rendered as grid buttons.
  Doesn't include a Web Browser entry - see "Tech decisions" below.
- `browser_kiosk.py` - standalone kiosk web browser. Not in
  `apps.json`: `ui/main_window.py`'s `_load_apps` appends a "Web
  Browser" card dynamically, only when
  `/var/lib/familyos/browser-visible` exists (toggled via the Parent
  Panel's "Show Browser on Main Screen" control, default OFF - see
  `../parental-tools/familyos-browser-toggle`), then launches it the
  same `subprocess.Popen` way as every other grid app. See "Tech
  decisions" below for why this is a custom `QWebEngineView` rather
  than a full browser app.

## Running (dev)

    pip install -r requirements.txt
    python3 main.py

Not runnable/screenshot-tested in this checkout's environment (no X11
display available here) - verified here only via `python3 -m
py_compile` and manual review. A real QEMU boot test of the CI-built
ISO has since happened (outside this environment) and found several
real bugs - see the parent-panel privilege-bug and display/UX fix
commits, and `docs/future-ideas.md` / `Browser.md` / `Flavor - Toddler.md`
for what that boot test surfaced.

## Tech decisions

- **PyQt5 over PyQt6:** `Development Roadmap.md`'s Phase 1 line says
  "Python/PyQt," not PyQt6 specifically. PyQt5 has a materially better
  packaging track record on Devuan/Debian i386 (see
  `_Base Architecture Overview.md`'s i386/Atom target), which matters
  more here than being on the latest Qt major version. `python3-pyqt5`
  and `python3-pyqt5.qtwebengine` availability on daedalus's `amd64`
  index is confirmed (`devuan-build-docs/confirmed-package-sweep.txt`,
  and both installed successfully in the first real CI build); `i386`
  availability is still unconfirmed, since no `i386` build has been run
  yet (see `Readme.md`'s "Architecture support").
- **Auth is not implemented in this module.** The parent panel pipes
  the typed password via stdin to scripts in `/usr/local/bin/familyos-*`
  (invoked through `sudo`, not the `parental-tools/` source layout -
  see `../parental-tools/README.md`'s "Auth & privilege contract"),
  which perform the real PAM-backed check after sudo has already
  elevated them to root. The panel's own "Unlock" step (action buttons
  start disabled and only enable once `familyos-verify-auth` succeeds)
  is a UI-side convenience gate on top of that, not a second
  independent security boundary.
- **No visible way back to the toddler screen except a launched app's
  own quit path (usually Escape) or the parent panel's Close button.**
  A real QEMU boot test flagged Escape-to-quit as real but
  undiscoverable for a toddler. This comes from each launched app's own
  native behavior, not anything FamilyOS controls: `gcompris-qt` and
  `tuxpaint` both show their own quit-confirmation on Escape by
  default; `browser_kiosk.py` deliberately does NOT rely on this - it
  has its own visible "Done" button instead (see `browser_kiosk.py`'s
  `KioskWindow`). Adding an equivalent visible affordance for the two
  third-party apps would mean wrapping/overlaying them, not just a
  config change - logged as a future idea
  (`docs/future-ideas.md`) rather than built speculatively here.
- **`browser_kiosk.py` is a custom embedded `QWebEngineView`, not Min
  or Falkon.** `Browser.md` names Min Browser, but Min is
  Electron-based and has shipped no i386 build since Electron dropped
  32-bit Linux support (~2018) - a hard blocker for the i386/Eee PC
  target. Falkon (QtWebEngine-based, real i386 packaging) was the
  fallback candidate, but it has no native lockdown mode beyond a
  `--fullscreen` toggle - no way to actually disable new tabs or URL
  entry as `Browser.md` describes. A bare `QWebEngineView` has no
  browser-chrome layer at all (no menu, no keybindings, no toolbar
  unless this code adds one), so there's no escape hatch to audit away
  in the first place. See the file's own header comment for the full
  reasoning, and `parental-tools/README.md` for the DoH-bypass
  mitigation this depends on.
- **Web Browser is hidden from the toddler grid by default, and its
  homepage is a parent-curated tile page, not a hardcoded URL.**
  `Flavor - Toddler.md`'s app curation never included a browser; a real
  boot test's "should this need parent unlock" question is resolved by
  keeping it out of `config/apps.json` entirely and instead having
  `ui/main_window.py`'s `_load_apps` append a "Web Browser" card
  dynamically, gated on a marker file
  (`/var/lib/familyos/browser-visible`) the Parent Panel's "Show
  Browser on Main Screen: ON/OFF" pair toggles (unlock-gated like every
  other control there). An earlier round put a direct "Open Browser"
  launch button inside the Parent Panel instead of this toggle -
  corrected, since that made the browser reachable only from inside an
  already-unlocked panel and never actually visible on the toddler's
  own screen at all. The Parent Panel's separate "Allowed Websites"
  section (`familyos-sites`) still lets a parent add/remove sites, each
  one becoming both a tile on the browser's local homepage and an entry
  in `browser_kiosk.py`'s navigation allowlist, unaffected by the
  visibility toggle - see `Browser.md` and
  `devuan-build-docs/confirmed-browser-homepage-domains.txt` for the
  full architecture and domain research.
- **Icon paths resolve against an install root, not CWD.**
  `main_window.py`/`parent_panel.py`/`browser_kiosk.py` all anchor
  icon lookups to `Path(__file__).resolve().parent...` chains that
  land on `launcher/`'s own parent directory - `/opt/familyos/` in the
  installed image, the repo root in a dev checkout - since `graphics/`
  is a sibling of `launcher/` in both. Icons are loaded defensively
  (`.exists()` checked first): a missing icon degrades to a
  label-only/text-fallback button rather than crashing. See
  `graphics/ASSET_INVENTORY.md` for what's actually sourced vs.
  fallback vs. still-missing.
