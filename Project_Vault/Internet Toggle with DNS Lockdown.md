
# Net-Toggle Script Mechanics

## Objective
A lightweight system script (`/usr/local/bin/familyos-net-toggle`) executed by the Parental GUI to instantly cut or restore external internet access while preserving local network connectivity.

## Backend Implementation (iptables)
Instead of tearing down the wireless interface (which forces the parent to manually reconnect to Wi-Fi later), the script manipulates firewall rules using the local subnet mask.

### 1. Internet OFF State (Isolate WAN, Keep LAN)
When internet is toggled OFF, the script drops all traffic routing to external networks but explicitly permits local IP traffic (e.g., `192.168.x.x` ranges) so local educational assets or network configurations remain functional.

### Bash

```
# Flush existing rules and drop non-local traffic
sudo iptables -F OUTPUT
sudo iptables -A OUTPUT -d 127.0.0.1 -j ACCEPT
sudo iptables -A OUTPUT -d 192.168.0.0/16 -j ACCEPT
sudo iptables -A OUTPUT -j DROP
```

### 2. Internet ON State (Full Access)
When internet is toggled ON, the script clears the drop rule, allowing full passage through the pre-locked DNS servers.

### Bash

```
# Clear drops and allow standard outbound routing
sudo iptables -F OUTPUT
sudo iptables -A OUTPUT -j ACCEP
```

DNS:
193.110.81.1
185.253.5.1
208.67.222.123
208.67.220.123

Lock DNS:
chattr +i /etc/resolv.conf

Internet toggle:
iptables/nftables rules + systemctl networking
