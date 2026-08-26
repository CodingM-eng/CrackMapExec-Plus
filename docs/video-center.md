# Video Guide Center

The **Video Guide Center** (`--v`) is a signature feature of CrackMapExec+ designed to accelerate security education and CTF onboarding.

---

## Commands

```bash
# Interactive Video Center
crackmapexec+ --v

# Direct topic lookup
crackmapexec+ --v smb
crackmapexec+ --v ldap
crackmapexec+ --v winrm
crackmapexec+ --v ssh
crackmapexec+ --v modules
crackmapexec+ --v wizard
crackmapexec+ --v reporting
crackmapexec+ --v full-tutorial

# List all catalog topics
crackmapexec+ --v list

# Search topic titles and descriptions
crackmapexec+ --v search "active directory"

# Show Video Center help
crackmapexec+ --v --h
```

---

## Customizing the Catalog

Users can override or extend the video catalog by creating a custom YAML file at:

```text
~/.config/crackmapexec-plus/videos.yaml
```

Example format:

```yaml
smb:
  title: "Custom SMB Seminar Guide"
  url: "https://youtube.com/watch?v=VIDEO_ID"
  start: 143
  description: "SMB fundamentals and authorized lab workflow"
  tags: ["smb", "windows"]

custom-ctf:
  title: "HTB Forest Machine Walkthrough"
  url: "https://youtube.com/watch?v=VIDEO_ID"
  start: 45
  description: "Step-by-step AD Kerberos and LDAP guide"
  tags: ["ctf", "htb", "kerberos"]
```

URLs are automatically parsed and formatted with deep-link timestamp parameters (e.g. `&t=143s`).
