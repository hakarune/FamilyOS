#!/usr/bin/env python3
"""Renders /var/lib/familyos/homepage.html from /var/lib/familyos/allowed-sites.json.

Called by familyos-sites after every add/remove, and once at build time
(familyos.blend's blend_postinst) to generate the initial homepage
matching the seeded default site list. Not privileged itself - it only
writes inside /var/lib/familyos, which the caller (familyos-sites,
already running as root post-sudo) owns.

The generated page is what browser_kiosk.py's "Home" button and initial
HOME_URL point at (file:///var/lib/familyos/homepage.html) - see that
file's own comments for why this is the ONLY file: URL
acceptNavigationRequest allows through.
"""
import html
import json
import sys

SITES_FILE = "/var/lib/familyos/allowed-sites.json"
HOMEPAGE_FILE = "/var/lib/familyos/homepage.html"

TILE_COLORS = ["#2E7D32", "#F9A825", "#1565C0", "#AD1457", "#00838F", "#6A1B9A"]

PAGE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>FamilyOS</title>
<style>
  body {{
    margin: 0;
    background: #FFF8E1;
    font-family: sans-serif;
    display: flex;
    flex-wrap: wrap;
    align-content: flex-start;
    justify-content: center;
    padding: 40px 20px;
  }}
  a.tile {{
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    width: 220px;
    height: 140px;
    margin: 16px;
    border-radius: 20px;
    color: #FFFFFF;
    font-size: 26px;
    font-weight: bold;
    text-decoration: none;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  }}
</style>
</head>
<body>
{tiles}
</body>
</html>
"""

TILE_TEMPLATE = (
    '<a class="tile" style="background-color: {color};" href="{url}">{name}</a>\n'
)


def render() -> None:
    try:
        with open(SITES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        data = {"sites": []}

    tiles = []
    for index, site in enumerate(data.get("sites", [])):
        color = TILE_COLORS[index % len(TILE_COLORS)]
        tiles.append(
            TILE_TEMPLATE.format(
                color=color,
                url=html.escape(site.get("url", ""), quote=True),
                name=html.escape(site.get("name", "")),
            )
        )

    page = PAGE_TEMPLATE.format(tiles="".join(tiles))
    with open(HOMEPAGE_FILE, "w", encoding="utf-8") as f:
        f.write(page)


if __name__ == "__main__":
    render()
    sys.exit(0)
