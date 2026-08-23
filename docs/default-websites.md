# Default website list: scope and reasoning

The actual data lives in `overlays/etc/familyos/default-websites.json`
(seeded into `/var/lib/familyos/allowed-sites.json` at build time - see
`iso-builder/live-sdk/blends/familyos/familyos.blend`'s `blend_postinst`).
This document explains *why* those four sites, and why not others - not
the mechanism, which is covered in `Project_Vault/Browser.md` and
`devuan-build-docs/confirmed-browser-homepage-domains.txt`.

## The four defaults

1. **KidzSearch** (`kidzsearch.com`) - kid-safe search engine, the
   project's original default before this list existed.
2. **BRAVE+** (`watch.braveplus.com`) - a paid kids' streaming service.
   Requires an account/login (unlike the other three) - included
   anyway as a default because it's a recognizable, purpose-built kids'
   product a family may already subscribe to, not because it's
   free-to-use out of the box.
3. **Starfall** (`starfall.com`) - K-5 reading/math activities. Free
   core content, no login required, no advertising.
4. **Ducksters** (`ducksters.com`) - educational reference/games site
   for school-age kids. Free, no login required for core content - see
   "Known exception" below.

## Selection criteria

Every default was checked against the same bar before being added:

- **Ad-free** (or, where not, the exception is documented explicitly -
  see below). Third-party ad networks on a children's site are a real
  exposure risk regardless of COPPA-compliance claims - ad creative,
  targeting, and third-party trackers aren't things this project
  controls or can vet the way it can vet its own code.
- **Appropriate for children as young as 5** (matching
  `Project_Vault/Flavor - Toddler.md`'s low end and reaching toward the
  Kids & Homeschool flavor's, per `Flavor - Kids and Homeschool.md`).
- **Deliberately neutral on contested social, political, or religious
  topics.** Not because those topics don't matter - because this is a
  *default* seed for a general-purpose OS, not a platform for FamilyOS
  itself to take a position on them. A family of any religious,
  political, or cultural background should be able to boot this image
  and find the out-of-the-box web content unobjectionable on those
  grounds specifically. Sites that are otherwise excellent but organize
  content around a particular cultural, religious, or political
  viewpoint aren't disqualified from being *good* - they're just not
  right for a default every family is handed regardless of asking for
  it.

## Known exception: Ducksters carries third-party advertising

Confirmed directly from the site's own footer (Ducksters' free tier
discloses "ads powered by ... COPPA compliant Playwire Kid's Club") -
this fails the ad-free criterion above. The ad-free tier
("Ducksters Premium") requires a paid account created by an adult 18+,
which doesn't fit a no-signup default either. Flagged clearly rather
than silently excluded or silently shipped without disclosure: Ducksters
is included as a default despite this, as a deliberate, disclosed
exception - a parent who wants a fully ad-free default set can remove
it via the Parent Panel's "Allowed Websites" section in the same couple
of taps as removing anything else on this list (see "Removability"
below). This is the one criterion Ducksters doesn't meet; it was still
checked against, and passed, the login and neutrality criteria.

## This is a floor, not a ceiling

This list is intentionally short and conservative. That's not a
judgment that other commonly-recommended kids' sites aren't good - it's
that this project is only comfortable *defaulting* every family to a
site it has personally verified against the criteria above. Parents are
expected and encouraged to add their own approved sites via the Parent
Panel's "Allowed Websites" section - the default list is a safe,
minimal starting point, not the intended ceiling of what a family can
use.

## Sites considered but not included by default

- **PBS Kids, National Geographic Kids** - well-regarded, but not
  independently verified against the ad-free/neutrality bar above
  closely enough to include as a *default* (both carry sponsor/
  underwriting content in some sections that wasn't fully audited).
  Not a claim they're unsuitable - just not vetted to the standard this
  list holds itself to.
- **Khan Academy Kids** - carries real accessibility concerns for the
  youngest end of this project's target range: its interface and
  account/profile-selection flow skew toward literate,
  independently-navigating children, less so the 2-5 age range
  `Project_Vault/Flavor - Toddler.md` targets as this project's
  Priority 1 flavor. Worth adding for the (not yet built) Kids &
  Homeschool flavor's older audience; not a good fit as a Toddler-flavor
  default.

## Removability

Every entry in this list - all four defaults included - is stored in
`/var/lib/familyos/allowed-sites.json` with no "protected" or
"is-default" concept anywhere in the schema or in the add/remove code
(`parental-tools/lib/sites-edit.py`). A parent can remove any of these
four exactly the same way they'd remove a site they added themselves -
select it in the Parent Panel's "Allowed Websites" list and remove it.
Confirmed by reading that code directly, not assumed.
