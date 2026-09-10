# ==============================================================================
# CrackMapExec+ (CME+) PowerShell Production Installer for Windows
# Next-Generation Security Lab, CTF, and Educational Testing Framework
# ==============================================================================
[CmdletBinding()]
param(
    [switch]$Dev = $false
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) {
    Write-Host "  [+] $msg" -ForegroundColor Green
}

function Write-Warn($msg) {
    Write-Host "  [!] $msg" -ForegroundColor Yellow
}

function Write-Fail($msg) {
    Write-Host "  [-] $msg" -ForegroundColor Red
    exit 1
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "             CrackMapExec+ Windows Installer                " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Locate Python >= 3.11
$pythonCmd = $null
$candidates = @(
    "python",
    "py",
    "python3",
    "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "C:\Program Files\Python313\python.exe",
    "C:\Program Files\Python312\python.exe",
    "C:\Program Files\Python311\python.exe"
)

foreach ($cmd in $candidates) {
    if (-not $cmd) { continue }
    $exePath = $cmd
    if (-not (Test-Path $exePath -PathType Leaf)) {
        $found = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($found) { $exePath = $found.Source } else { continue }
    }
    try {
        $pInfo = Start-Process -FilePath $exePath -ArgumentList '-c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"' -NoNewWindow -Wait -PassThru -ErrorAction SilentlyContinue
        if ($pInfo.ExitCode -eq 0) {
            $pythonCmd = $exePath
            break
        }
    } catch { }
}

if (-not $pythonCmd) {
    Write-Fail "Python 3.11+ was not found in PATH. Please install Python 3.11 or newer."
}

$pyVer = & $pythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
Write-Info "Python runtime verified: $pythonCmd (v$pyVer)"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvDir = Join-Path $scriptDir ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

# 2. Virtual Environment Setup
if (Test-Path $venvPython) {
    try {
        & $venvPython -c "import sys; sys.exit(0)"
        if ($LASTEXITCODE -eq 0) {
            Write-Info "Existing virtual environment verified at $venvDir"
        } else {
            throw "Broken venv"
        }
    } catch {
        Write-Warn "Existing .venv is broken. Recreating cleanly..."
        Remove-Item -Recurse -Force $venvDir -ErrorAction SilentlyContinue
        & $pythonCmd -m venv $venvDir
    }
} else {
    Write-Info "Creating dedicated virtual environment at $venvDir..."
    & $pythonCmd -m venv $venvDir
}

if (-not (Test-Path $venvPython)) {
    Write-Fail "Virtual environment Python executable not found at $venvPython"
}

# 3. Upgrade pip and install package
Write-Info "Upgrading pip, setuptools, and wheel in virtual environment..."
& $venvPython -m pip install --quiet --upgrade pip setuptools wheel

Write-Info "Installing CrackMapExec+..."
if ($Dev) {
    & $venvPython -m pip install --quiet -e "$scriptDir[dev]"
} else {
    & $venvPython -m pip install --quiet -e $scriptDir
}

$cmeVer = & $venvPython -c "import cmeplus; print(cmeplus.__version__)"
Write-Info "Package installed and verified: cmeplus v$cmeVer"

# 4. Create Root and User-Local Batch Wrappers
$wrapperNames = @("crackmapexec+", "cme+", "crackmapexec-plus", "cme-plus", "crackmapexecplus", "cmeplus")

# A. Create .cmd in repo root
foreach ($name in $wrapperNames) {
    $cmdPath = Join-Path $scriptDir "$name.cmd"
    $cmdContent = @"
@echo off
"$venvPython" -m cmeplus.cli.parser %*
"@
    Set-Content -Path $cmdPath -Value $cmdContent -Encoding ASCII
}
Write-Info "Repository launchers ready (.cmd in $scriptDir)"

# B. Create in %USERPROFILE%\.local\bin
$userBin = Join-Path $env:USERPROFILE ".local\bin"
if (-not (Test-Path $userBin)) {
    New-Item -ItemType Directory -Path $userBin -Force | Out-Null
}

foreach ($name in $wrapperNames) {
    $userCmdPath = Join-Path $userBin "$name.cmd"
    $cmdContent = @"
@echo off
"$venvPython" -m cmeplus.cli.parser %*
"@
    Set-Content -Path $userCmdPath -Value $cmdContent -Encoding ASCII
}
Write-Info "Installed standalone launchers into $userBin"

# 5. Verify Installation
Write-Info "Verifying execution outside activated environment..."
$testVer = & "$scriptDir\crackmapexec+.cmd" --version
Write-Info "Execution verification: $testVer"

Write-Host ""
Write-Host "Installation succeeded!" -ForegroundColor Green
Write-Host "You can run CrackMapExec+ from the repo directory or from any directory if $userBin is in your PATH:"
Write-Host "  .\crackmapexec+ --version" -ForegroundColor Cyan
Write-Host "  .\crackmapexec+ doctor" -ForegroundColor Cyan
Write-Host "  .\cme+ --demo" -ForegroundColor Cyan
