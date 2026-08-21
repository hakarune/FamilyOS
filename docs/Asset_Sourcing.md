# Icon & Asset Sourcing

Design decision, recorded before Phase 4 (Branding & ISO Mastering)
execution. Governs where `graphics/`'s icon assets come from -
including the icons already referenced by placeholder path in
`launcher/config/apps.json` (`graphics/icons/gcompris.svg`,
`tuxpaint.svg`, `media-player.svg`, `browser.svg`) and any future
parent-facing UI icons.

## The split

FamilyOS has two distinct audiences with different icon needs, so it
uses two different icon sets rather than one:

| Audience | Source | License |
| --- | --- | --- |
| **Kid-facing** - launcher app grid, Toddler flavor UI | [sugar-artwork](https://github.com/sugarlabs/sugar-artwork) (Sugar Labs) | Apache License 2.0 |
| **Parent-facing** - Parent Dashboard, settings, system UI | [Papirus icon theme](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme) | GPL-3.0 |

**Why sugar-artwork for kids:** it's a glyph-style icon set purpose-built
for young children as part of the OLPC/Sugar learning platform -
actively maintained, not a defunct project - so it's a better fit for
the Toddler/Kids flavor's target age range (`Project_Vault/Flavor -
Toddler.md`, `Project_Vault/Flavor - Kids and Homeschool.md`) than a
general-purpose icon theme designed for adult desktop use.

**Why Papirus for parents:** already the project's existing choice for
general desktop iconography (`Project_Vault/Graphics Modernization.md`
already lists it as a tool), well-maintained, broad application
coverage - appropriate for the Parent Dashboard, which is a normal
adult-oriented settings UI, not a kid-facing surface.

## Fallback order

sugar-artwork won't cover every icon the launcher needs (e.g.
app-specific icons for apps outside the Sugar activity ecosystem, like
a generic media player or web browser icon). When an icon is missing
from sugar-artwork:

1. Fall back to Papirus for that specific icon.
2. If Papirus doesn't have an appropriate match either, generate a
   simple on-theme placeholder SVG matching sugar-artwork's glyph
   style (flat, bold, high-contrast) until a proper asset is sourced
   or designed.

This is a per-icon fallback, not a blanket rule - most kid-facing
icons should still come from sugar-artwork; Papirus/placeholder is the
exception path, not a parallel default.

## Licensing & attribution

Both licenses require attribution if FamilyOS is ever redistributed,
but their terms differ - don't treat them as interchangeable:

- **Apache License 2.0** (sugar-artwork): requires retaining
  copyright/license notices, including a copy of the license text, and
  stating any significant changes made to the licensed files.
  Permissive - does not require FamilyOS itself to be Apache-licensed.
- **GPL-3.0** (Papirus): requires retaining copyright/license notices
  and providing the license text alongside the assets. FamilyOS is
  already GPL-v3 licensed as a whole (per the root `LICENSE` file), so
  this is compatible without extra complication - but the Papirus
  icons' own attribution should still be called out specifically
  (project name, source URL, license), not just folded silently into
  FamilyOS's own copyright notice.

This is a practical attribution checklist, not legal advice - a formal
license review is recommended before any public redistribution.

**Action item for Phase 4 execution (not done as part of this
docs-only update):** add a `NOTICE` or `ATTRIBUTION.md` file under
`graphics/` listing both projects, their source URLs, and their
license terms, alongside the actual vendored/downloaded icon files.

## Addendum (Phase 4 execution): sugar-artwork has no app-icon coverage

Phase 4 execution found that sugar-artwork's actual contents are a
toolkit/action glyph set for the Sugar activity shell (copy, save,
go-home, media transport, battery/network status), not an
application-icon set - its `apps/` category contains exactly one icon.
It has no matches for GCompris, Tux Paint, a generic media player, or
a generic web browser, since none of these are Sugar activities. In
practice, every current kid-facing app-grid icon is a Papirus fallback
via the documented fallback order, not a sugar-artwork original - see
`graphics/ASSET_INVENTORY.md` for the full breakdown. This doesn't
invalidate the sourcing split above (sugar-artwork may still be the
right call for other kid-facing UI elements as the Toddler/Kids
flavors grow), but the app-grid-icon premise specifically didn't hold
and shouldn't be assumed to in future planning.
