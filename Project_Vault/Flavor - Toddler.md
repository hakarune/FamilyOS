# Flavor Profile: Toddler (Priority 1)

## Target Audience
Ages 2 to 5. Entirely non-text, mouse/trackpad, or touch-driven.

## Desktop Environment & Window Management
- **Window Manager:** Openbox (Standalone, no panel, no desktop icons, no dock).
- **Lockdown Rules (`rc.xml` modifications):**
  - Disable right-click desktop menu.
  - Disable all global keybindings (`Alt+Tab`, `Alt+F4`, `Super/Windows Key`, `Alt+Space`).
  - Disable window borders, title bars, and window dragging.
  - All applications are forced to launch center-screen, borderless, and maximized.

## Primary Interface (The FamilyOS Launcher)
- **Execution:** Launched automatically via `~/.xinitrc` on X11 start.
- **Technology:** Fullscreen, borderless PyQt6 or GTK3 application.
- **UI Blueprint:**
  - Hardcoded layout optimized to scale dynamically down to **1024x600** and **800x480** (Eee PC specifications).
  - Uses a fluid, non-scrolling grid of massive button cards displaying custom high-contrast SVG icons (Papirus/Numix based).
  - No status bar, no close button, no exit paths.
  - Clicking a button launches its corresponding application via a subprocess. When the application closes, the user is seamlessly returned to the menu grid.
  - **Parental Control Access:** Features a secured, low-profile anchor button for parents. On activation, it prompts for authentication.
  - **Embedded Parent GUI:** Contains a dedicated, restricted control panel layout allowing parents to toggle internet access, adjust master volume caps, change wireless networks, or gracefully reboot/shutdown the machine via oversized, clear buttons.
  

## App Curation (i386 and amd64 Compatible)
- GCompris (Educational suite - launched with no CLI args, which is
  GCompris-qt's own default behavior for opening its full activity
  selection menu, not a single activity. GCompris-qt ships roughly 100
  built-in activities across reading, math, memory/matching, logic,
  and science categories, so the toddler grid's single "GCompris"
  button already exposes all of that content - it's not a
  single-activity shortcut. See `launcher/config/apps.json`.)
- Tux Paint (Drawing)
- TuxMath (tux4kids arcade math game - falling-problem, Missile
  Command-style gameplay)
- TuxTyping (tux4kids typing tutor - includes alphabet/finger-position
  practice modes usable before real typing matters)
- Pinned local audio/video player pointing to an offline media folder.

**Confirmed complete** (first QEMU boot-test round raised "only ~3 kid
apps visible" as a possible missing-content bug): `launcher/config/apps.json`
implements this curation - this is the full, intentional set for this
flavor, not a partial/broken subset. The Kids & Homeschool flavor
(`Flavor - Kids and Homeschool.md`, ages 5+, Priority 2) would carry
its own, separate, larger app set - it hasn't been built yet. A Web
Browser entry used to also be present in `apps.json` despite not being
part of this list at all - resolved (removed from `apps.json` entirely;
a "Web Browser" card is appended to the grid dynamically instead, only
when a parent has turned it on via the Parent Panel's "Show Browser on
Main Screen" toggle, default OFF) - see `Browser.md`.

**ChildsPlay was researched and rejected, not overlooked:** it would
have been a strong match for "matching/memory game" requests (its
suite includes exactly that), but it does not exist as an installable
package anywhere in Devuan daedalus's main, contrib, or non-free
archives - confirmed against a real download of all three
`Packages.gz` indexes. It only appears as a stale `Suggests:` entry
inside a handful of unrelated packages' metadata, not as an actual
`Package:` stanza - the package was dropped from the Debian archive
years before daedalus (bookworm-based) existed. No dedicated
open-source "Go Fish," "Guess Who," or "Battleship" Tux-branded title
was found to exist either - not fabricated or substituted here.