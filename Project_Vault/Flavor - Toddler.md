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
- GCompris (Educational suite)
- Tux Paint (Drawing)
- Pinned local audio/video player pointing to an offline media folder.

**Confirmed complete** (first QEMU boot-test round raised "only ~3 kid
apps visible" as a possible missing-content bug): `launcher/config/apps.json`
implements exactly these three - this is the full, intentional curation
for this flavor, not a partial/broken subset. The Kids & Homeschool
flavor (`Flavor - Kids and Homeschool.md`, ages 5+, Priority 2) would
carry its own, separate, larger app set - it hasn't been built yet. A
Web Browser entry used to also be present in `apps.json` despite not
being part of this list at all - resolved (removed from the toddler
grid entirely, moved to the Parent Panel) - see `Browser.md`.