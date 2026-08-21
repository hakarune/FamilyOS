# Flavor Profiles: Kids, STEM, & Homeschool (Priority 2)

## Target Audience
Ages 5+. Text-literate, requiring a traditional desktop metaphor but retaining tight guardrails.

## Desktop Environment: XFCE Lockdown Strategy
Unlike the Toddler flavor, these versions utilize a modified XFCE environment. To prevent kids from breaking out, XFCE must be locked down using system-wide default profiles and restricted permissions:

### 1. Panel & Menu Lockdown (`Kiosk Mode`)
- Utilize XFCE's built-in kiosk mode by creating a system-wide restriction profile at `/etc/xdg/xfce4/kiosk/kioskrc`.
- **Restrictions Enforced:**
```ini
  [xfce4-panel]
  CustomizePanel=NONE
  
  [xfce4-session]
  Shutdown=NONE
  Reboot=NONE