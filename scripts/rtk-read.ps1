# rtk-read.ps1 — print a file through RTK's compressor, if RTK is installed locally.
# Falls back with a clear message if .tools\rtk\rtk.exe is absent.
# Usage:  .\scripts\rtk-read.ps1 <path>
$root = Split-Path -Parent $PSScriptRoot
$exe  = Get-ChildItem -Path (Join-Path $root '.tools\rtk') -Filter 'rtk*.exe' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $exe) {
    Write-Error "RTK not installed locally. Run .\scripts\install-rtk-local.ps1 first (see its trust note)."
    exit 1
}
# Adjust subcommand to match the installed RTK version (`rtk --help`).
& $exe.FullName run -- Get-Content @args
exit $LASTEXITCODE
