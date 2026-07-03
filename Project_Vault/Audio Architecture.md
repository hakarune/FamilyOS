# FamilyOS Audio Architecture

## Core Engine: ALSA (Advanced Linux Sound Architecture)
To maximize compatibility and eliminate CPU overhead on 10-to-15-year-old single-core hardware (i386/Atom), FamilyOS bypasses heavy sound daemons like PipeWire or PulseAudio. Audio is routed directly through native kernel ALSA drivers.

## System Configurations & Locks
1. **Default State:** The system will use standard `alsa-utils` for sound management.
2. **The Toddler Volume Cap:** To protect child hearing and hardware speakers, a hard cap is written directly to the ALSA state configuration file (`/var/lib/alsa/asound.state`).
3. **Parent Control Hook:** The Embedded Parent GUI adjusts master volume using backend terminal commands rather than a desktop audio applet:
```bash
   # Set hard ceiling to 65% max system volume
   amixer set Master 65%
   ```
   
## 2. The Net-Toggle Script Mechanics
Your files mention a `net-toggle` script several times, but you haven't given the AI the actual blueprint of *how* that script should behave. If the parent clicks "Internet: OFF" in the GUI, how does the system block the web without breaking the local network (like connecting to a local school server or network printer)?