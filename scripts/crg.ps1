# crg.ps1 — project-local wrapper for code-review-graph
#
# Usage:   .\scripts\crg.ps1 build
#          .\scripts\crg.ps1 status
#          .\scripts\crg.ps1 detect-changes
#
# Runs code-review-graph from this repo's .venv, storing its graph in the
# project-local .crg\ directory. Does NOT touch global config.
# NOTE: never run `crg.ps1 install` / `init` here — those register a GLOBAL MCP
# server. This wrapper blocks them on purpose.

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$exe  = Join-Path $root '.venv\Scripts\code-review-graph.exe'

if (-not (Test-Path $exe)) {
    Write-Error "code-review-graph not found at $exe. Run the venv setup first."
    exit 1
}

if ($args.Count -ge 1 -and ($args[0] -eq 'install' -or $args[0] -eq 'init')) {
    Write-Error "Blocked: '$($args[0])' registers a GLOBAL MCP server. Not allowed in this project-local setup."
    exit 1
}

# Pin repo root and project-local data dir so the graph never leaks globally.
& $exe @args --repo $root --data-dir (Join-Path $root '.crg')
exit $LASTEXITCODE
