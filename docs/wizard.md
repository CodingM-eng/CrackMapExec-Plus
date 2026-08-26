# Interactive Wizard

The **Interactive Wizard** (`crackmapexec+ wizard`) provides a guided terminal prompt for building and running tasks without memorizing CLI syntax.

---

## Usage

```bash
crackmapexec+ wizard
```

---

## Workflow Steps

1. **Target Input**: Enter single IP, CIDR (`192.168.1.0/24`), range, or `@file.txt`.
2. **Protocol Selection**: Choose from `smb`, `ldap`, `winrm`, `ssh`, or `mock`.
3. **Authentication**: Optionally specify username, password, or domain.
4. **Modules**: Interactively select enumeration modules (e.g. `shares`, `users`).
5. **Workers**: Set concurrency pool size.
6. **Execution**: Review the formatted job summary and confirm execution.

The wizard compiles user selections directly into a standard `Job` object and dispatches it to the Core Engine.
