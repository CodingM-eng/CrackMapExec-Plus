export interface ParsedCommand {
  raw: string;
  command: string;
  args: string[];
  flags: Record<string, string | boolean>;
  isValid: boolean;
  securityViolation?: boolean;
}

const ALLOWED_COMMANDS = new Set([
  "help",
  "target",
  "scan",
  "nmap",
  "smb",
  "ldap",
  "winrm",
  "ssh",
  "inspect",
  "history",
  "clear",
  "cme+",
  "crackmapexec+",
]);

const DANGEROUS_PATTERNS = [
  "&&", ";", "|", "`", "$", "<", ">",
  "bash", "sh", "zsh", "exec", "eval", "system",
  "sudo", "su", "chmod", "chown", "curl", "wget",
  "python", "python3", "perl", "ruby", "node",
  "cat", "ls", "pwd", "rm", "mv", "cp", "echo",
  "javascript:", "alert(", "document.", "window.", "process.env",
  "/etc/", "c:\\\\", "\\\\windows\\\\", "localhost", "127.0.0.1",
];

export function parseTerminalInput(input: string): ParsedCommand {
  const trimmed = input.trim();
  if (!trimmed) {
    return { raw: "", command: "", args: [], flags: {}, isValid: true };
  }

  const lower = trimmed.toLowerCase();
  for (const pattern of DANGEROUS_PATTERNS) {
    if (lower.includes(pattern)) {
      return {
        raw: trimmed,
        command: "",
        args: [],
        flags: {},
        isValid: false,
        securityViolation: true,
      };
    }
  }

  // Tokenize arguments cleanly without shell interpretation
  const tokens = trimmed.split(/\s+/);
  let cmd = tokens[0].toLowerCase();
  let args = tokens.slice(1);

  // If user enters 'cme+ smb ...' or 'crackmapexec+ smb ...', unwrap sub-command
  if (cmd === "cme+" || cmd === "crackmapexec+") {
    if (args.length === 0) {
      cmd = "help";
    } else {
      cmd = args[0].toLowerCase();
      args = args.slice(1);
    }
  }

  if (!ALLOWED_COMMANDS.has(cmd)) {
    return {
      raw: trimmed,
      command: cmd,
      args,
      flags: {},
      isValid: false,
    };
  }

  const flags: Record<string, string | boolean> = {};
  const positionalArgs: string[] = [];

  for (let i = 0; i < args.length; i++) {
    const token = args[i];
    if (token.startsWith("--")) {
      const key = token.slice(2);
      if (i + 1 < args.length && !args[i + 1].startsWith("-")) {
        flags[key] = args[i + 1];
        i++;
      } else {
        flags[key] = true;
      }
    } else if (token.startsWith("-")) {
      const key = token.slice(1);
      if (i + 1 < args.length && !args[i + 1].startsWith("-")) {
        flags[key] = args[i + 1];
        i++;
      } else {
        flags[key] = true;
      }
    } else {
      positionalArgs.push(token);
    }
  }

  return {
    raw: trimmed,
    command: cmd,
    args: positionalArgs,
    flags,
    isValid: true,
  };
}
