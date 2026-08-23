#!/usr/bin/env python3
"""Add/remove entries in /var/lib/familyos/allowed-sites.json.

Invoked by familyos-sites (already root, already past
require_parent_auth) - not meant to be run standalone. Each entry
stores the host FamilyOS's kiosk browser will actually check
navigation against (launcher/browser_kiosk.py's ALLOWED_HOSTS is loaded
straight from this file's "host" fields) - deriving it here, once, at
add time, rather than trusting a parent-typed value or re-deriving it
in the browser at every navigation check.
"""
import json
import sys
from urllib.parse import urlparse

USAGE = "usage: sites-edit.py {add <file> <name> <url> | remove <file> <host>}"


def load(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        data = {}
    data.setdefault("sites", [])
    return data


def save(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def add(path: str, name: str, url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        print(f"Rejected: '{url}' is not a valid http:// or https:// URL", file=sys.stderr)
        sys.exit(1)
    host = parsed.hostname.lower()

    data = load(path)
    data["sites"] = [s for s in data["sites"] if s.get("host") != host]
    data["sites"].append({"name": name, "url": url, "host": host})
    save(path, data)


def remove(path: str, host: str) -> None:
    data = load(path)
    host = host.lower()
    before = len(data["sites"])
    data["sites"] = [s for s in data["sites"] if s.get("host") != host]
    if len(data["sites"]) == before:
        print(f"No entry found for host '{host}'", file=sys.stderr)
        sys.exit(1)
    save(path, data)


def main() -> None:
    if len(sys.argv) < 3:
        print(USAGE, file=sys.stderr)
        sys.exit(1)

    command, path = sys.argv[1], sys.argv[2]
    if command == "add" and len(sys.argv) == 5:
        add(path, sys.argv[3], sys.argv[4])
    elif command == "remove" and len(sys.argv) == 4:
        remove(path, sys.argv[3])
    else:
        print(USAGE, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
