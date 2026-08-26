# Video Guide Center

The **Video Guide Center** (`--video` / `--v`) is a signature feature of CrackMapExec+ designed to accelerate security education, CTF onboarding, and protocol workflow mastery.

---

## 1. Video Invocation

* **Primary Command**: `crackmapexec+ --video`
* **Short Alias**: `crackmapexec+ --v`

Both commands invoke the exact same Video Guide Engine.

---

## 2. Topic Commands

Directly inspect metadata, start timestamps, status, and direct URLs for any protocol or framework workflow:

```bash
# Core Protocols
crackmapexec+ --video smb
crackmapexec+ --video ldap
crackmapexec+ --video winrm
crackmapexec+ --video ssh

# Framework Features
crackmapexec+ --video modules
crackmapexec+ --video wizard
crackmapexec+ --video reporting
crackmapexec+ --video installation
crackmapexec+ --video introduction

# Using Short Alias
crackmapexec+ --v smb
crackmapexec+ --v ldap
```

---

## 3. Video Statuses & "Coming Soon" Behavior

Video catalog entries support two primary lifecycle statuses:
1. `coming_soon`: The tutorial is in active preparation.
   - When requested (e.g. `crackmapexec+ --video smb`), CrackMapExec+ outputs a polished status panel:
     ```text
     ╭──────────────────────────────────────────────╮
     │          CrackMapExec+ Video Guide           │
     ╰──────────────────────────────────────────────╯

     Topic:
     SMB

     Status:
     🚧 Coming Soon

     This tutorial is currently being prepared.

     Video:
     https://youtube.com/watch?v=VIDEO_ID

     Start time:
     02:23

     When published, this command will automatically
     open the tutorial at the SMB section.
     ```
   - Placeholder URLs are **not** opened automatically in the browser.
2. `published`: The tutorial has been published.
   - Deep-linked URLs with calculated timestamps (e.g. `https://youtube.com/watch?v=VIDEO_ID&t=143s`) are presented.
   - In interactive terminals, users can press ENTER to automatically launch the default browser at the exact topic offset.

---

## 4. Library Listing & Search

### List All Topics
```bash
crackmapexec+ --video list
crackmapexec+ --v list
```

Renders a Rich table:
```text
╭────────────────────────────────────────────────────────────────────────╮
│                          Video Guide Library                           │
╰────────────────────────────────────────────────────────────────────────╯
Topic          Status          Start       Title
──────────────────────────────────────────────────────────────────────────
SMB            Coming Soon     02:23       SMB Guide
LDAP           Coming Soon     06:15       LDAP Guide
WinRM          Coming Soon     10:42       WinRM Guide
SSH            Coming Soon     14:20       SSH Guide
Modules        Coming Soon     17:00       Modules Guide
Wizard         Coming Soon     18:30       Wizard Guide
Reporting      Coming Soon     21:15       Reporting & Dashboards
Installation   Coming Soon     00:45       Installation & Setup Guide
Introduction   Coming Soon     00:00       Introduction to CrackMapExec+
```

### Search Topics and Descriptions
```bash
crackmapexec+ --video search smb
crackmapexec+ --v search "active directory"
```

Searches topic keys, titles, descriptions, status, and keywords, returning matching results with execution recommendations.

---

## 5. Customizing the Video Catalog

Users can customize or extend the catalog by placing a `videos.yaml` file at:

```text
~/.config/crackmapexec-plus/videos.yaml
```

### Schema (`videos.yaml`):

```yaml
smb:
  title: "SMB Guide"
  status: "coming_soon"
  url: "https://youtube.com/watch?v=VIDEO_ID"
  start_seconds: 143
  description: "SMB fundamentals, dialect negotiation, and authorized lab workflow"
  keywords: ["smb", "windows", "shares", "signing"]

custom_kerberos:
  title: "Kerberos Roasting Guide"
  status: "published"
  url: "https://youtube.com/watch?v=CUSTOM_ID"
  start_seconds: 95
  description: "SPN enumeration and TGS request walkthrough"
  keywords: ["kerberos", "ad", "tgs"]
```

> [!NOTE]
> The timestamp parameter `&t=143s` is dynamically calculated at runtime from `start_seconds: 143` and is never hardcoded.
