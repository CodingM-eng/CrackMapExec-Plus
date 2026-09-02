export interface ReleaseItem {
  version: string;
  isLatest?: boolean;
  date: string;
  tag: string;
  title: string;
  highlights: string[];
  githubUrl: string;
  assets: { name: string; url: string }[];
}

export const releasesData: ReleaseItem[] = [
  {
    version: "v0.1.0",
    isLatest: true,
    date: "2026-08-28",
    tag: "v0.1.0",
    title: "CrackMapExec+ v0.1.0 — Architecture Upgrade & Nmap Intelligence",
    highlights: [
      "First-Class Nmap Intelligence Engine (-oN parser, resolver, preview plan)",
      "Universal TransportEngine with explicit 8-stage connection state machine",
      "SMB deep NTLMSSP TargetInfo AV_PAIR extraction and dialect negotiation",
      "LDAP RootDSE naming context extraction and SASL mechanism discovery",
      "WinRM WS-Man WWW-Authenticate challenge header interrogation",
      "SSH RFC 4253 banner analysis and OS distribution heuristics",
      "10-Point Doctor Diagnostics (update --check, doctor, dev doctor)",
      "Privacy-conscious automated bug tracking with fingerprint deduplication",
      "Zero plaintext credential persistence on disk",
      "Interactive Guided Wizard and 100% offline safe Demo Mode",
    ],
    githubUrl: "https://github.com/CodingM-eng/CrackMapExec-Plus/releases/tag/v0.1.0",
    assets: [
      { name: "crackmapexec-plus-0.1.0.tar.gz", url: "https://github.com/CodingM-eng/CrackMapExec-Plus/archive/refs/tags/v0.1.0.tar.gz" },
      { name: "crackmapexec-plus-0.1.0.zip", url: "https://github.com/CodingM-eng/CrackMapExec-Plus/archive/refs/tags/v0.1.0.zip" },
      { name: "crackmapexec-plus_0.1.0-1_all.deb", url: "https://github.com/CodingM-eng/CrackMapExec-Plus/releases/download/v0.1.0/crackmapexec-plus_0.1.0-1_all.deb" },
    ],
  },
];
