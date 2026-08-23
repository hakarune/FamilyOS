# FamilyOS Web Sandbox Architecture

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
