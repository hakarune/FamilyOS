# Future ideas (not implemented - discuss before building)

Logged from the first real QEMU boot-test round. Neither of these has
been built - they need a product discussion first, not just an
implementation.

## Parent-toggleable allowed-apps list

A "Manage apps" section in the Parent Panel where a parent can toggle
which of the launcher's configured apps actually show up in the
toddler grid (`launcher/config/apps.json`), rather than the app set
being fixed at build time. Would need: a persisted, parent-writable
config separate from the read-only `apps.json` shipped in the image
(the live root is squashfs - anything user-toggleable needs to land in
the overlay/persistence layer, not the base image), and UI in
`parent_panel.py` to edit it.

## Visible "return to launcher" affordance over third-party apps

Right now, getting back to the launcher grid from GCompris or Tux Paint
relies on each app's own native Escape-to-quit-confirm behavior -
undiscoverable for a toddler, and not something FamilyOS's own code
provides (unlike `browser_kiosk.py`, which has an explicit visible
"Done" button since it's FamilyOS's own code). A persistent, low-profile
overlay/watchdog window (echoing the launcher's own "low-profile parent
anchor" convention) could provide a consistent, visible way back for
every app, not just the browser - but that means wrapping or overlaying
third-party GUI apps FamilyOS doesn't control, not a small config
change. Flagged during the first QEMU boot-test round
(`launcher/README.md`'s "Tech decisions").

## Multiple interface/theme flavors

DoudouLinux reportedly ships several UI styles/complexity levels
(different visual themes and/or interaction complexity for different
ages) under one project, rather than one fixed interface. Worth
considering as a future flavor system alongside the already-planned
Toddler / Kids & Homeschool split
(`Project_Vault/Flavor - Toddler.md`, `Project_Vault/Flavor - Kids and
Homeschool.md`) - e.g. letting a parent pick a complexity/visual level
within a flavor rather than only across flavors.
