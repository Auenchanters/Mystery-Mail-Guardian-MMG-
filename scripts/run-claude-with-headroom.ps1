# run-claude-with-headroom.ps1 — launch Claude Code behind a project-local Headroom proxy.
#
# ⚠️ STATUS ON THIS MACHINE: NOT FUNCTIONAL YET.
#    headroom-ai publishes Python wheels for macOS/Linux only — there is NO
#    Windows wheel. Installing it on Windows compiles a Rust extension, which
#    needs a Rust toolchain (cargo/rustc) = a global install (~/.cargo, ~/.rustup).
#    That was deliberately NOT done (project-local-only policy). See HANDOFF.md.
#
#    To make this work, pick one (with approval):
#      - install Rust via rustup, then: uv pip install --python .venv\Scripts\python.exe "headroom-ai[proxy]"
#      - OR run the whole setup under WSL/Linux where prebuilt wheels exist.
#
# Once headroom.exe exists in the venv, this script starts the proxy and points
# Claude at it via SESSION-SCOPED env vars only (no global Claude config edits).

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$hr   = Join-Path $root '.venv\Scripts\headroom.exe'

if (-not (Test-Path $hr)) {
    Write-Error @"
Headroom is not installed in this project's .venv (no Windows wheel; needs a Rust
toolchain to build). See the note at the top of this script and HANDOFF.md.
Aborting so nothing global is touched.
"@
    exit 1
}

$port = 8787
Write-Host "Starting Headroom proxy on http://127.0.0.1:$port ..."
$proxy = Start-Process -FilePath $hr -ArgumentList @('proxy','--port',"$port") -PassThru -NoNewWindow

try {
    # Session-scoped only: these env vars vanish when this PowerShell session ends.
    $env:ANTHROPIC_BASE_URL = "http://127.0.0.1:$port"
    Write-Host "Launching Claude Code (ANTHROPIC_BASE_URL scoped to this session)..."
    claude @args
}
finally {
    if ($proxy -and -not $proxy.HasExited) { Stop-Process -Id $proxy.Id -Force }
    Remove-Item Env:\ANTHROPIC_BASE_URL -ErrorAction SilentlyContinue
}
