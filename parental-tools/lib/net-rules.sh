#!/bin/bash
# Shared FamilyOS network-filtering rules, applied atomically via plain
# `iptables-restore` (no --noflush - its chain-replacement semantics
# for built-in chains are undocumented; FamilyOS owns the whole filter
# table on this appliance anyway, so a full-table replace is both
# simpler and unambiguous: the man page confirms default mode flushes
# the entire table before loading).
#
# Fail-safe default: internet is OFF until a parent explicitly enables
# it (see familyos-net-toggle and the familyos-net-lock boot script,
# overlays/etc/init.d/familyos-net-lock) - a hard power-cycle is always
# possible and outside software's control, so landing in "no WAN"
# after ANY reboot is the safer state for a kid-safety product.
#
# Callers must source lib/env-guard.sh before this file (for
# is_dry_run) - not sourced automatically here to keep this file
# focused/composable.

# Known public DoH resolvers, blocked in BOTH states as
# defense-in-depth against DNS-lockdown bypass. The primary mitigation
# is disabling DoH in the browser itself (see
# launcher/browser_kiosk.py's QTWEBENGINE_CHROMIUM_FLAGS) - this is a
# backstop against anything else that might try, and is NOT an
# exhaustive list. See parental-tools/README.md.
_FAMILYOS_DOH_BLOCK_RULES="
-A OUTPUT -d 1.1.1.1 -j DROP
-A OUTPUT -d 1.0.0.1 -j DROP
-A OUTPUT -d 8.8.8.8 -j DROP
-A OUTPUT -d 8.8.4.4 -j DROP
-A OUTPUT -d 9.9.9.9 -j DROP"

apply_net_state() {
    local state="$1"
    local rules

    case "$state" in
        on)
            rules="*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
${_FAMILYOS_DOH_BLOCK_RULES}
COMMIT"
            ;;
        off)
            rules="*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT DROP [0:0]
-A OUTPUT -o lo -j ACCEPT
-A OUTPUT -d 10.0.0.0/8 -j ACCEPT
-A OUTPUT -d 172.16.0.0/12 -j ACCEPT
-A OUTPUT -d 192.168.0.0/16 -j ACCEPT
${_FAMILYOS_DOH_BLOCK_RULES}
COMMIT"
            ;;
        *)
            echo "apply_net_state: unknown state '$state' (want on|off)" >&2
            return 1
            ;;
    esac

    if is_dry_run; then
        echo "[DRY RUN] would apply via iptables-restore:"
        echo "$rules"
    else
        echo "$rules" | iptables-restore
    fi
}
