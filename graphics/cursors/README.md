# graphics/cursors

Scaffolded but empty by design - no cursor theme requirement appears
in any Project_Vault doc (`_Base Architecture Overview.md`, `Flavor -
Toddler.md`, `Flavor - Kids and Homeschool.md`, `Graphics
Modernization.md`). This directory exists because the Phase 4 task
brief's example folder structure named it, not because a specific
cursor asset has been decided on.

Open question for a future decision, not answered here: does the
Toddler flavor need a custom (larger/higher-contrast) cursor theme for
touch/young-child usability, or does the standard X11 default cursor
suffice given the Launcher's massive touch targets already do most of
the accessibility work? Neither `sugar-artwork` nor `papirus-icon-theme`
is a cursor theme, so this would need a third source (or a decision
that no custom cursor is needed) if pursued - see
`docs/Asset_Sourcing.md`, which does not currently cover cursors.
