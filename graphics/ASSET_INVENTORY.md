# graphics/ Asset Inventory

Compiled per `docs/Asset_Sourcing.md`'s sourcing decision, Phase 4
(Branding & ISO Mastering). Every graphical asset the project needs,
where it actually came from, and its license status - so nothing is
silently left as an unflagged generic shape.

## Important finding: sugar-artwork has no usable matches for the app-grid icons

`docs/Asset_Sourcing.md` designated sugar-artwork as the kid-facing
icon source. In practice, after cloning the real repo and inspecting
its actual contents (`icons/scalable/{actions,apps,categories,control,
device,emblems,mimetypes,status}/`), **its `apps/` category contains
exactly one icon (`activity-journal.svg`)** - sugar-artwork is a
toolkit/action glyph set for the Sugar activity shell (copy, save,
zoom, go-home, media transport controls, battery/network status
icons), not an application-icon set. It has zero coverage for
GCompris, Tux Paint, a generic media player, or a generic web browser
- none of these are Sugar activities, so none have a sugar-artwork
icon to fall back FROM.

This isn't a broken plan - it's the documented fallback order
(sugar-artwork → Papirus → placeholder) doing exactly its job. But the
realistic outcome is that **all four app-grid icons are Papirus
fallbacks**, not sugar-artwork originals, and that should be stated
plainly rather than implied otherwise. sugar-artwork's actual
contribution to this project is currently zero vendored files - its
role is limited to style/palette reference for the hand-authored
custom branding (see below), which is a reference use, not a vendored
one, and doesn't carry the same attribution obligation as copying
actual files.

## Kid-facing icons — `graphics/icons/kids/`

| File | App | Source | License | Status |
| --- | --- | --- | --- | --- |
| `gcompris.svg` | GCompris | Papirus `64x64/apps/gcompris.svg` | GPL-3.0 | Fallback (no sugar-artwork match) |
| `tuxpaint.svg` | Tux Paint | Papirus `64x64/apps/tuxpaint.svg` | GPL-3.0 | Fallback (no sugar-artwork match) |
| `media-player.svg` | Media Player | Papirus `64x64/devices/multimedia-player.svg` | GPL-3.0 | Fallback (no sugar-artwork match) |
| `browser.svg` | Web Browser | Papirus `64x64/apps/internet-web-browser.svg` (via the `browser.svg` alias) | GPL-3.0 | Fallback (no sugar-artwork match) |

## Parent-facing icons — `graphics/icons/parent/`

| File | Used by | Source | License | Status |
| --- | --- | --- | --- | --- |
| `network-wireless.svg` | Internet ON/OFF buttons | Papirus `64x64/devices/network-wireless.svg` | GPL-3.0 | Sourced as designed |
| `volume.svg` | Set Volume Cap | Papirus `24x24/panel/audio-volume-high.svg` | GPL-3.0 | Sourced as designed |
| `reboot.svg` | Reboot button | Papirus `64x64/apps/system-reboot.svg` | GPL-3.0 | Sourced as designed |
| `shutdown.svg` | Shutdown button | Papirus `64x64/apps/system-shutdown.svg` | GPL-3.0 | Sourced as designed |
| `lock.svg` | Parent panel password field, Change Password button | Papirus `64x64/apps/system-lock-screen.svg` | GPL-3.0 | Sourced as designed |
| `folder.svg` | Remount RW (media folder) | Papirus `64x64/places/folder-blue.svg` (via the `folder.svg` alias) | GPL-3.0 | Sourced as designed |
| `close.svg` | Browser kiosk "Done" button | Papirus `22x22/actions/window-close.svg` | GPL-3.0 | Sourced as designed |

`settings.svg` (Launcher's parent-anchor button) was originally sourced
this same way (Papirus `64x64/apps/utilities-tweak-tool.svg`) but has
since been **replaced with a hand-authored icon** - see "Custom/original
assets" below for why and what it looks like now. Every other file in
this table is still the original Papirus sourcing, unchanged - this
project's established "kid-facing vs. parent-facing" split
(`docs/Asset_Sourcing.md`) still holds for icons that only ever appear
inside the already-unlocked, deliberately plain/adult-styled Parent
Panel; `settings.svg` was the one exception because it's visible on the
toddler's own home screen, not inside that dialog.

All remaining Papirus files fetched individually (not a full repo
clone - the upstream repo is ~361MB, disproportionate to vendor
wholesale into a lean distro source tree). Several of the requested
filenames turned out to be symlinks in the upstream repo to a
differently-named real file (`browser.svg` → `internet-web-browser.svg`,
`folder.svg` → `folder-blue.svg`); the table above notes both names
where that happened. All files verified as well-formed XML
(`xmllint --noout` / `python3 -m xml.dom.minidom`).

## Custom/original assets — not sourced from either icon pack

| Asset | Location | Notes |
| --- | --- | --- |
| FamilyOS logo/wordmark | `graphics/branding/familyos-logo.svg` (+ rendered `.png` at 512/128px) | Hand-authored. Style cues (flat fills, bold outlines, no gradients, high contrast) taken from sugar-artwork's visual language for family resemblance, but not derived from any specific sugar-artwork file. |
| Plymouth boot splash | `graphics/splash/` (`familyos.plymouth`, `familyos.script`, `familyos-logo.png`) | Minimal "script"-plugin theme: solid background + centered logo, no animated progress bar (kept simple since the Plymouth script interpreter can't be run in this authoring environment to test against - see `iso-builder/live-build/README.md`). |
| Toddler background | `graphics/wallpapers/toddler-background.svg` | Low priority - the Launcher runs fullscreen at all times per `Flavor - Toddler.md`, so this is rarely actually visible. Flat solid color, not a design investment beyond that. |
| Parent-anchor icon | `graphics/icons/parent/settings.svg` | Replaces a generic flat Papirus Material-style icon (a real boot test called it "boring") - a cartoonish padlock with a small heart cutout echoing the main logo's own heart motif, so it reads as the same brand family. Hand-authored for the same reason as the logo above: this icon is visible on the toddler's own home screen (the low-profile parent anchor), unlike every other Papirus icon in `icons/parent/`, which only appears inside the already-unlocked, deliberately plain/adult-styled Parent Panel. |
| Kiosk decorative background | `graphics/branding/kiosk-background-tile.svg` (+ rendered `kiosk-background-tile.png`) | A real boot test called the overall kiosk look "boring/gray" and asked for an actual colorful, playful, kid-facing visual design (DoudouLinux/Qimo4kids spirit). Sparse, soft-pastel scattered shapes (stars, a cloud, dots) on a transparent background, designed to tile seamlessly (verified by rendering a 2x2 composite) at any target screen resolution rather than a single fixed-size scene image. Deliberately sparse/low-contrast-with-itself - kept as gentle decoration behind the much higher-contrast app-grid buttons, not a busy texture, avoiding any seizure-risk/visual-noise pattern on a screen a toddler looks at for extended periods. |

## Explicitly open / not delivered this phase

- **Cursor theme** (`graphics/cursors/`): scaffolded directory + README only. No Project_Vault doc specifies a cursor requirement; this was requested in the Phase 4 task's example folder structure, not the architecture docs. Left as an open design question rather than inventing an unrequested asset - see `graphics/cursors/README.md`.
- **sugar-artwork LICENSE/COPYING**: not vendored into `graphics/LICENSES/`, since zero sugar-artwork files were actually used (see the finding above). If a future icon need is found that sugar-artwork *does* cover, add its license at that point - attribution is required for what's actually used, not for a library merely consulted for style reference. For the record: sugar-artwork's repo root contains two license files with no explanation of their relative scope - `LICENSE` (Apache License 2.0, matching GitHub's own auto-detected repo license and `docs/Asset_Sourcing.md`'s documented choice) and `COPYING` (LGPL-2.1). Worth a closer look if sugar-artwork files are vendored later.

## License files preserved

- `graphics/LICENSES/papirus-icon-theme.LICENSE` - GPL-3.0, full upstream text.
