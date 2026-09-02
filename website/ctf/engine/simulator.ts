import { Challenge } from "../challenges/types";
import { parseTerminalInput } from "./command-parser";

export interface SimulationResult {
  output: string;
  isError?: boolean;
  clearTerminal?: boolean;
}

export function executeSimulation(
  input: string,
  challenge: Challenge,
  history: string[]
): SimulationResult {
  const parsed = parseTerminalInput(input);

  if (parsed.securityViolation || !parsed.isValid) {
    return {
      output: `\x1b[31mUnknown command. Type "help" to see available CrackMapExec+ CTF commands.\x1b[0m`,
      isError: true,
    };
  }

  if (parsed.command === "clear") {
    return { output: "", clearTerminal: true };
  }

  if (parsed.command === "history") {
    if (history.length === 0) {
      return { output: "No previous commands in session history." };
    }
    const lines = history.map((item, idx) => `  ${(idx + 1).toString().padStart(3, " ")}  ${item}`);
    return { output: `Session Command History:\n${lines.join("\n")}` };
  }

  if (parsed.command === "help") {
    return {
      output: `\x1b[36m╭──────────────── CrackMapExec+ Virtual Terminal ────────────────╮\x1b[0m
\x1b[36m│\x1b[0m Available simulation commands:
\x1b[36m│\x1b[0m   \x1b[32mhelp\x1b[0m                  Display this command reference
\x1b[36m│\x1b[0m   \x1b[32mtarget\x1b[0m                Display current simulated target information
\x1b[36m│\x1b[0m   \x1b[32mnmap <ip>\x1b[0m             Run Nmap Intelligence on simulated target
\x1b[36m│\x1b[0m   \x1b[32msmb <ip> [options]\x1b[0m    Interrogate SMB service, shares, and metadata
\x1b[36m│\x1b[0m   \x1b[32mldap <ip>\x1b[0m             Query LDAP RootDSE naming context & SASL
\x1b[36m│\x1b[0m   \x1b[32mwinrm <ip>\x1b[0m            Probe WinRM HTTP service and auth schemes
\x1b[36m│\x1b[0m   \x1b[32mssh <ip>\x1b[0m              Inspect SSH banner and identification
\x1b[36m│\x1b[0m   \x1b[32minspect <port/path>\x1b[0m   Inspect specific service payload or HTTP endpoint
\x1b[36m│\x1b[0m   \x1b[32mhistory\x1b[0m               Show session command history
\x1b[36m│\x1b[0m   \x1b[32mclear\x1b[0m                 Clear terminal display
\x1b[36m╰─────────────────────────────────────────────────────────────────╯\x1b[0m
\x1b[33m[!] Note: All operations run inside an isolated educational sandbox.\x1b[0m`,
    };
  }

  if (parsed.command === "target") {
    return {
      output: `\x1b[36m╭────────────────── Assigned Simulated Target ──────────────────╮\x1b[0m
\x1b[36m│\x1b[0m Target IP:       \x1b[32m${challenge.targetIp}\x1b[0m
\x1b[36m│\x1b[0m Hostname:        \x1b[33m${challenge.targetHostname}\x1b[0m
\x1b[36m│\x1b[0m Environment:     \x1b[34mVirtual Sandboxed Lab\x1b[0m
\x1b[36m│\x1b[0m Objective:       ${challenge.objective.en}
\x1b[36m╰───────────────────────────────────────────────────────────────╯\x1b[0m
\x1b[33m[!] SIMULATED TARGET: No external network traffic is generated.\x1b[0m`,
    };
  }

  const targetArg = parsed.args[0] || challenge.targetIp;

  if (parsed.command === "nmap" || parsed.command === "scan") {
    const serviceRows = challenge.services
      .map(
        (s) =>
          `\x1b[32m${s.port.toString().padEnd(6, " ")}/tcp\x1b[0m  \x1b[33m${s.state.padEnd(7, " ")}\x1b[0m  \x1b[36m${s.service.padEnd(14, " ")}\x1b[0m  ${s.version}`
      )
      .join("\n");

    const mappedWorkflows = challenge.services
      .map((s) => {
        if (s.port === 445 || s.port === 139) return `  ${s.port}/tcp  MICROSOFT-DS  \x1b[32m✓  Native SMB driver\x1b[0m`;
        if (s.port === 389 || s.port === 636) return `  ${s.port}/tcp  LDAP          \x1b[32m✓  Native LDAP driver\x1b[0m`;
        if (s.port === 5985 || s.port === 5986) return `  ${s.port}/tcp  WSMAN         \x1b[32m✓  Native WinRM driver\x1b[0m`;
        if (s.port === 22) return `  ${s.port}/tcp  SSH           \x1b[32m✓  Native SSH driver\x1b[0m`;
        if (s.port === 80 || s.port === 443) return `  ${s.port}/tcp  HTTP          \x1b[33m✓  Web Service Inspection (use 'inspect 80')\x1b[0m`;
        return `  ${s.port}/tcp  ${s.service.toUpperCase()}  \x1b[33m⚠  Unmapped service\x1b[0m`;
      })
      .join("\n");

    return {
      output: `\x1b[34m[*] Starting Nmap Intelligence Scan against ${targetArg}...\x1b[0m
\x1b[32m[+] Host ${challenge.targetHostname} (${challenge.targetIp}) is UP (0.0019s latency)\x1b[0m

PORT        STATE    SERVICE         VERSION
──────────────────────────────────────────────────────────────────────────
${serviceRows}

\x1b[36m╭──────────── CrackMapExec+ Nmap Intelligence ────────────╮\x1b[0m
Discovered Services:
${mappedWorkflows}

\x1b[32m[+] Intelligence scan complete. Target mapped for further investigation.\x1b[0m`,
    };
  }

  // CHALLENGE 1: forgotten-endpoint
  if (challenge.id === "forgotten-endpoint") {
    if (parsed.command === "smb") {
      return {
        output: `\x1b[36m╭──────────────────────────────────────────────────────────────╮\x1b[0m
\x1b[36m│ SMB • ${challenge.targetIp}:445                                      │\x1b[0m
\x1b[36m╰──────────────────────────────────────────────────────────────╯\x1b[0m
STATUS        \x1b[32m[+] SUCCESS\x1b[0m
HOST          ${challenge.targetHostname}
OS            Ubuntu 22.04 LTS (Samba 4.15)
SMB DIALECT   SMB 3.1.1
SIGNING       Disabled
SMBv1         False

\x1b[34m[*] Enumerating Accessible Shares (Anonymous Session):\x1b[0m
  Share:      \x1b[32mpublic\x1b[0m          (Read Only)
  Share:      \x1b[33mWebConfig$\x1b[0m      (Read Only) -> Note: Contains apache-vhost.conf backup
  Share:      IPC$            (Default IPC)

\x1b[33m[!] Tip: Run 'inspect WebConfig$' or 'inspect 80' to inspect web service parameters.\x1b[0m`,
      };
    }

    if (parsed.command === "inspect") {
      const arg = parsed.args.join(" ").toLowerCase();
      if (arg.includes("webconfig") || arg.includes("conf") || arg.includes("vhost")) {
        return {
          output: `\x1b[34m[*] Reading WebConfig$/apache-vhost.conf backup...\x1b[0m
<VirtualHost *:80>
    ServerName portal.corp.internal
    DocumentRoot /var/www/portal/public
    
    # Internal Debugging Route (DO NOT EXPOSE TO EXTERNAL)
    # Temporary dev status proxy:
    ProxyPass /api/v1/internal-status http://127.0.0.1:8080/status
</VirtualHost>

\x1b[32m[+] Discovered hidden debugging route: /api/v1/internal-status\x1b[0m
\x1b[33m[!] Execute 'inspect /api/v1/internal-status' to query the shadow endpoint!\x1b[0m`,
        };
      }

      if (arg.includes("/api/v1/internal-status") || arg.includes("internal-status") || arg === "8080") {
        return {
          output: `\x1b[34m[*] HTTP GET http://${challenge.targetIp}/api/v1/internal-status\x1b[0m
\x1b[32mHTTP/1.1 200 OK\x1b[0m
Content-Type: application/json; charset=utf-8
Server: Apache/2.4.52 (Ubuntu)
X-Internal-Service: Portal-Telemetry-Worker-1

{
  "service": "Portal Telemetry & Node Health",
  "status": "ONLINE",
  "node_id": "lab-portal-alpha-09",
  "debug_flag": "\x1b[32m${challenge.canonicalFlag}\x1b[0m",
  "timestamp": "2026-09-02T12:00:00Z"
}

\x1b[32m[+] FLAG DISCOVERED! Copy the flag and submit it in the Flag Vault below.\x1b[0m`,
        };
      }

      return {
        output: `\x1b[34m[*] HTTP GET http://${challenge.targetIp}:80/\x1b[0m
\x1b[32mHTTP/1.1 200 OK\x1b[0m
Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html>
  <head><title>Internal Portal Login</title></head>
  <body>
    <h1>Corporate Portal Node</h1>
    <p>Notice: This node is currently undergoing maintenance.</p>
    <!-- Check SMB WebConfig$ share for migration notes -->
  </body>
</html>

\x1b[33m[!] Tip: Check the SMB 'WebConfig$' share or run 'inspect WebConfig$'\x1b[0m`,
      };
    }

    if (parsed.command === "ldap" || parsed.command === "winrm" || parsed.command === "ssh") {
      return {
        output: `\x1b[31m[-] Port for ${parsed.command.toUpperCase()} is not listening on ${challenge.targetIp}.\x1b[0m
\x1b[33m[!] Use 'nmap ${challenge.targetIp}' to check available services.\x1b[0m`,
        isError: true,
      };
    }
  }

  // CHALLENGE 2: ghost-headers
  if (challenge.id === "ghost-headers") {
    if (parsed.command === "winrm") {
      return {
        output: `\x1b[36m╭──────────────────────────────────────────────────────────────╮\x1b[0m
\x1b[36m│ WinRM • ${challenge.targetIp}:5985                                   │\x1b[0m
\x1b[36m╰──────────────────────────────────────────────────────────────╯\x1b[0m
STATUS        \x1b[32m[+] REACHABLE (HTTP 401 Unauthorized)\x1b[0m
SERVER        Microsoft-HTTPAPI/2.0
WS-MAN VER    2.0
AUTH SCHEMES  Negotiate, NTLM
X-DEBUG-ENV   Staging-Lab-Node-09
X-INTERNAL-TK Y21lK3tnaG9zdF9tZXRhZGF0YV9sZWFrZWRfaW5faGVhZGVyc30=

\x1b[33m[!] Staging telemetry detected in HTTP response headers!\x1b[0m
\x1b[33m[!] Tip: Use 'inspect 5985' or 'inspect headers' to decode the base64 token.\x1b[0m`,
      };
    }

    if (parsed.command === "inspect") {
      return {
        output: `\x1b[34m[*] Analyzing HTTP Response Headers from http://${challenge.targetIp}:5985/wsman...\x1b[0m

HTTP/1.1 401 Unauthorized
Content-Length: 0
Server: Microsoft-HTTPAPI/2.0
WWW-Authenticate: Negotiate
WWW-Authenticate: NTLM
X-Debug-Environment: Staging-Lab-Node-09
X-Build-Origin: ci-runner-44
X-Internal-Token: \x1b[33mY21lK3tnaG9zdF9tZXRhZGF0YV9sZWFrZWRfaW5faGVhZGVyc30=\x1b[0m
Date: Wed, 02 Sep 2026 12:00:00 GMT

\x1b[34m[*] Decoding X-Internal-Token Base64 Payload:\x1b[0m
\x1b[32m[+] Decoded Token: ${challenge.canonicalFlag}\x1b[0m

\x1b[32m[+] FLAG DISCOVERED! Copy the flag and submit it in the Flag Vault below.\x1b[0m`,
      };
    }

    if (parsed.command === "smb" || parsed.command === "ldap" || parsed.command === "ssh") {
      return {
        output: `\x1b[31m[-] Port for ${parsed.command.toUpperCase()} is closed/filtered on ${challenge.targetIp}.\x1b[0m
\x1b[33m[!] Use 'nmap ${challenge.targetIp}' to check active ports (Hint: WinRM is on 5985).\x1b[0m`,
        isError: true,
      };
    }
  }

  // CHALLENGE 3: broken-gateway
  if (challenge.id === "broken-gateway") {
    if (parsed.command === "ldap") {
      return {
        output: `\x1b[36m╭──────────────────────────────────────────────────────────────╮\x1b[0m
\x1b[36m│ LDAP • ${challenge.targetIp}:389                                     │\x1b[0m
\x1b[36m╰──────────────────────────────────────────────────────────────╯\x1b[0m
STATUS        \x1b[32m[+] REACHABLE (RootDSE Query Successful)\x1b[0m
NAMING CTX    \x1b[33mDC=gateway,DC=sec,DC=lab\x1b[0m
DNS HOSTNAME  GATEWAY-DC01.sec.lab
SASL MECHS    GSSAPI, GSS-SPNEGO, NTLM
TLS REQUIRED  False
SERVICE ACCTS \x1b[32msvc_router_mgmt\x1b[0m, Administrator, krbtgt

\x1b[34m[*] Active Directory Domain Controller verified.\x1b[0m
\x1b[33m[!] Run 'smb ${challenge.targetIp}' to enumerate domain shares for svc_router_mgmt backups.\x1b[0m`,
      };
    }

    if (parsed.command === "smb") {
      return {
        output: `\x1b[36m╭──────────────────────────────────────────────────────────────╮\x1b[0m
\x1b[36m│ SMB • ${challenge.targetIp}:445                                      │\x1b[0m
\x1b[36m╰──────────────────────────────────────────────────────────────╯\x1b[0m
STATUS        \x1b[32m[+] SUCCESS (Anonymous / Null Session Enabled)\x1b[0m
HOST          GATEWAY-DC01
OS            Windows Server 2022 Datacenter (Build 20348)
DOMAIN        SEC.LAB
SIGNING       False

\x1b[34m[*] Accessible Domain Shares:\x1b[0m
  Share:      SYSVOL          (Read Only)
  Share:      NETLOGON        (Read Only)
  Share:      \x1b[32mRouterBackup$\x1b[0m   (Read Only) -> Contains gateway recovery keys

\x1b[33m[!] Run 'inspect RouterBackup$' to examine the router backup configuration file!\x1b[0m`,
      };
    }

    if (parsed.command === "inspect") {
      return {
        output: `\x1b[34m[*] Connecting to SMB \\\\10.13.37.100\\RouterBackup$...\x1b[0m
\x1b[32m[+] File Retrieved: router-recovery.conf\x1b[0m

# =======================================================
# GATEWAY DC01 - EMERGENCY ROUTER RECOVERY CONFIGURATION
# Generated by: sec.lab\\svc_router_mgmt
# =======================================================
[Router_Authentication]
Management_Protocol = SSH (Port 22)
Recovery_Token      = \x1b[32m${challenge.canonicalFlag}\x1b[0m
Allowed_Subnets     = 10.13.37.0/24

\x1b[32m[+] FINAL FLAG DISCOVERED! Master challenge solved.\x1b[0m
\x1b[32m[+] Submit the flag below to complete the CrackMapExec+ Mini-CTF track!\x1b[0m`,
      };
    }

    if (parsed.command === "ssh") {
      return {
        output: `\x1b[36m╭──────────────────────────────────────────────────────────────╮\x1b[0m
\x1b[36m│ SSH • ${challenge.targetIp}:22                                       │\x1b[0m
\x1b[36m╰──────────────────────────────────────────────────────────────╯\x1b[0m
STATUS        \x1b[32m[+] OPEN\x1b[0m
BANNER        SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6
PROTOCOL VER  2.0
AUTH REQUIRED Public Key / Password

\x1b[33m[!] Tip: Check LDAP and SMB 'RouterBackup$' share for recovery credentials.\x1b[0m`,
      };
    }

    if (parsed.command === "winrm") {
      return {
        output: `\x1b[31m[-] WinRM port 5985 is closed on ${challenge.targetIp}. (Target uses SSH on Port 22).\x1b[0m`,
        isError: true,
      };
    }
  }

  return {
    output: `\x1b[33m[*] Command '${parsed.raw}' executed on simulated target ${targetArg}.\x1b[0m
\x1b[33m[!] Type 'help' to see available commands for this challenge.\x1b[0m`,
  };
}
