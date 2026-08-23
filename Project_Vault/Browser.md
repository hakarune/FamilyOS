# FamilyOS Web Sandbox Architecture

**Resolved: browser is parent-gated, not a toddler-grid app.** The
"should this be reachable without parent unlock" open question from the
first boot-test round is resolved: `launcher/config/apps.json` no longer
lists a Web Browser entry at all (matching `Flavor - Toddler.md`'s own
three-app curation, which never included one), and the Parent Panel
(`launcher/ui/parent_panel.py`) now has an "Open Browser" button instead -
disabled, like every other control there, until a parent unlocks the
panel.

**Curated homepage, not a single fixed site.** The browser's home page
is no longer a hardcoded `kidzsearch.com` URL - it's a locally generated
tile page (`/var/lib/familyos/homepage.html`) rendered from a
parent-editable site list (`/var/lib/familyos/allowed-sites.json`,
managed via the Parent Panel's "Allowed Websites" section ->
`parental-tools/familyos-sites`). Seeded by default with KidzSearch and
BRAVE+ (`watch.braveplus.com`, a paid kids' streaming service) so the
Toddler flavor works out of the box. A "Home" button in the browser
always returns to this page. Full research trail (CDN/embed domain
findings, what the allowlist mechanism does and doesn't actually cover):
`devuan-build-docs/confirmed-browser-homepage-domains.txt`.

**Navigation lockdown confirmed, and extended to cover the whole
curated list, not just one hardcoded host.** `launcher/browser_kiosk.py`'s
`AllowlistPage.acceptNavigationRequest` still confirms every navigation
(typed - moot, no URL bar; clicked; JS-redirected; and iframe loads,
since `is_main_frame` is deliberately not special-cased) is checked
against a host allowlist and rejected otherwise, non-http(s) schemes are
blocked outright (with one narrow exception: the local homepage file,
matched by exact resolved path, not just scheme), and `createWindow`
returning `None` blocks popup/new-window escape hatches. The allowlist
itself is now loaded from `allowed-sites.json` at process start (every
host a parent adds is automatically covered), plus a small, separate,
non-parent-editable set of known video-embed hosts
(`www.youtube.com`/`www.youtube-nocookie.com`, needed for KidzTube's
YouTube-embedded videos to render at all - see the domains doc above for
why). **Important scope clarification found this round**: this
allowlist governs navigation/frame loads, NOT an already-loaded allowed
page's own sub-resource network calls (video segments, XHR/fetch, ads,
trackers) - those were never gated by this mechanism, in either
direction; the system-level DNS lockdown and DoH blocklist remain the
actual defense against that traffic class. See the domains doc for the
full reasoning and what's still open (BRAVE+ playback and KidzTube's
"Watch on YouTube" escape-link risk, both flagged as needing a real
login/playback test, not assumed either safe or broken).

**Implementation status:** the engine choice below (Min) is this design
doc's original candidate and was **not** what got built. Min is
Electron-based and has shipped no `i386` build since Electron dropped
32-bit Linux support (~2018) - a hard blocker for this project's Eee-PC
`i386` target - and Falkon (the fallback candidate) has no lockdown mode
beyond a `--fullscreen` toggle. What actually ships is a custom embedded
`QWebEngineView` (`launcher/browser_kiosk.py`), with no browser-chrome
layer at all rather than a full browser app with a lockdown mode. See
`launcher/README.md`'s "Tech decisions" for the full reasoning. The
lockdown *goals* described below (inescapable fullscreen, no URL bar, no
new tabs) still apply - they're just achieved by omission (nothing to
disable) rather than a Focus Mode setting.

## Core Engine: Min Browser (superseded - see status note above)
Min is selected as the primary web engine for the Toddler flavor due to its minimal user interface, built-in tracker/ad blocking, low RAM footprint on 10-year-old hardware, and native 32-bit (i386) compatibility.

## UI Lockdown Configuration (Focus Mode)
To ensure toddlers cannot wander off-site or break the browser interface, Min must be launched via the FamilyOS Launcher with specific runtime environment profiles and automation scripts.

### 1. Inescapable Window Management
When a web activity is launched from the FamilyOS launcher, the background `openbox` window manager forces the window to be borderless, fullscreen, and centered, with all navigation keybindings completely disabled.

### 2. Enforcing Interface Restrictions
Min will be launched directly into its native **Focus Mode**. This dynamically locks the interface to prevent typical user breaking points:
- Hides the main navigation bar and window frame.
- Disables the creation of new tabs or browser tasks.
- Restricts URL bar entry completely so toddlers cannot manually input web addresses.
- Auto-blocks third-party tracking networks, scripts, and flashing advertisements.

## Network & DNS Guardian Integration
The browser's security relies heavily on the system's underlying networking layers configured by the parent:

1. **The Content Filter:** System-wide fallback DNS routing is hardcoded in `/etc/resolv.conf` to safe-search networks (KidzSearch / CleanBrowsing / OpenDNS Family).
2. **The WAN Interrupter:** When the parent toggles Internet to "OFF" in the Parent Dashboard, a backend system script executes local networking cutoffs:
```
   bash
   # System script executed by parent GUI to isolate the machine locally
   sudo iptables -A OUTPUT -p tcp --dport 80 -j DROP
   sudo iptables -A OUTPUT -p tcp --dport 443 -j DROP
```
   

Falkon config overrides:
[General]
allowIncognito=false
searchProvider=kidzsearch.com
forceDNS=193.110.81.1
