# graphics

Branding assets, icons, and the Plymouth boot theme. Per
`docs/Asset_Sourcing.md`'s sourcing decision:

- `icons/kids/` - kid-facing app-grid icons. Currently all sourced as
  Papirus fallbacks, not sugar-artwork originals - see
  `ASSET_INVENTORY.md`'s "Important finding" section for why.
- `icons/parent/` - parent-facing dashboard/settings icons, Papirus.
- `branding/` - the original FamilyOS logo/wordmark (hand-authored,
  not from either icon pack).
- `splash/` - the Plymouth boot theme (installed to
  `/usr/share/plymouth/themes/familyos` at build time - see
  `iso-builder/live-sdk/blends/familyos/familyos.blend`'s
  `blend_postinst`, or `iso-builder/live-build/README.md` for the
  superseded equivalent).
- `wallpapers/` - Toddler flavor background (low priority - see
  `ASSET_INVENTORY.md`).
- `cursors/` - scaffolded, no asset delivered - see its own README.
- `LICENSES/` - upstream license text for any icon set actually
  vendored (currently: Papirus only).

**Full asset-by-asset inventory, sources, and license status:** see
`ASSET_INVENTORY.md` in this directory - it lists every file, its
source, its license, and flags every fallback/placeholder explicitly.

## Attribution

This project vendors icons from the Papirus icon theme
(github.com/PapirusDevelopmentTeam/papirus-icon-theme), licensed
GPL-3.0 - see `LICENSES/papirus-icon-theme.LICENSE` for the full text.
FamilyOS is itself GPL-v3 licensed (see the root `LICENSE` file), so
this is compatible without extra complication, but Papirus's own
attribution (project name, source URL, license) should be called out
specifically wherever this image is redistributed - not silently
folded into FamilyOS's own copyright notice. See
`docs/Asset_Sourcing.md` for the full licensing/attribution rationale,
including why Apache-2.0-licensed sugar-artwork isn't currently listed
here (no files from it are actually vendored yet).
