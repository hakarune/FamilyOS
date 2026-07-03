Suggested Project Structure:

familyos-devuan/
├── iso-builder/            # Live-build / Refracta build configurations
├── overlays/               # Files to be injected directly into the live ISO root
│   ├── etc/
│   │   ├── X11/xorg.conf.d/# Graphic tweaks for old hardware
│   │   ├── resolv.conf     # Immutable DNS settings
│   │   ├── network/        # net-toggle script hooks
│   │   └── openbox/        # rc.xml (completely stripped of shortcuts)
│   └── home/
│       ├── toddler/
│       │   ├── .xinitrc    # Launches the kiosk environment on login
│       │   └── .config/
│       └── parent/         # Password-protected admin home
├── launcher/               # Source code for the custom toddler fullscreen menu (Python/PyQt)
├── parental-tools/         # Python/Bash scripts for net-toggle and RW remounting
├── graphics/               # SVGs, Plymouth themes, and branding
├── docs/
└── README.md