# FamilyOS Web Sandbox Architecture

**Navigation lockdown confirmed (first QEMU boot-test round):** a code
review of `launcher/browser_kiosk.py`'s `AllowlistPage.acceptNavigationRequest`
confirms the toddler genuinely cannot navigate off `kidzsearch.com`/
`www.kidzsearch.com` - every navigation (typed, clicked, or JS-redirected)
is checked against a host allowlist and rejected otherwise, non-http(s)
schemes are blocked outright, and `createWindow` returning `None` blocks
popup/new-window escape hatches. There is no URL bar at all (bare
`QWebEngineView`, no browser chrome), so there's nothing to type into in
the first place. This was a real open question in the boot-test report
(is it actually enforced, or just a kid-safe homepage default a toddler
could type away from?) - confirmed by code review to be the former, not
the latter. Not yet confirmed by actually clicking an external link
during a live boot test - recommended as a quick follow-up.

**Open question raised by the same boot-test round:** should this
browser even be reachable from the toddler grid without parent unlock at
all? `Project_Vault/Flavor - Toddler.md`'s own "App Curation" list names
only three apps (GCompris, Tux Paint, a local media player) - no
browser - so its presence in `launcher/config/apps.json` goes beyond
that flavor's original spec, regardless of how well-locked-down it is.
Not resolved here - needs a product decision (keep as-is since it's
already safe; gate behind parent unlock as defense-in-depth; or reserve
browser access for the not-yet-built Kids/Homeschool flavor instead).

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
