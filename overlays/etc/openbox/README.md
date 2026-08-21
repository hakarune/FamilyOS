# overlays/etc/openbox

Superseded: the Openbox lockdown config now lives at
`overlays/home/toddler/.config/openbox/rc.xml` (per-user, toddler-scoped)
rather than a system-wide path, since only the toddler session needs
the lockdown rules - see that file's own header comment for the
rationale. This directory is kept as a placeholder in case a genuinely
system-wide Openbox default is ever needed (e.g. a shared default for
both toddler and parent sessions), but nothing currently uses it.
