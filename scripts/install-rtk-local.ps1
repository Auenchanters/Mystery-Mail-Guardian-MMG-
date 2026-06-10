# install-rtk-local.ps1 — fetch a prebuilt RTK Windows binary into THIS repo only.
#
# ⚠️  TRUST NOTE: RTK (https://github.com/rtk-ai/rtk) is a third-party Rust binary.
#     This script downloads and unpacks an .exe from GitHub Releases into
#     .tools\rtk\ — i.e. it brings third-party executable code onto your machine.
#     Review the repo/release before running. RTK is NOT on npm; the commonly
#     posted `npm install -g @rtk-ai/rtk` does not exist.
#
# It installs LOCALLY (no global PATH change, no Homebrew, no cargo, no init -g).
# Usage:  .\scripts\install-rtk-local.ps1
# After:  use .\scripts\rtk-grep.ps1 etc., or .tools\rtk\rtk.exe directly.

$ErrorActionPreference = 'Stop'
$root    = Split-Path -Parent $PSScriptRoot
$dest    = Join-Path $root '.tools\rtk'
New-Item -ItemType Directory -Force -Path $dest | Out-Null

Write-Host "Querying latest RTK release from GitHub..."
$rel = Invoke-RestMethod -Uri 'https://api.github.com/repos/rtk-ai/rtk/releases/latest' `
                         -Headers @{ 'User-Agent' = 'rtk-local-install' }

# Find a Windows x86_64 asset (zip/exe). Adjust the pattern if RTK changes naming.
$asset = $rel.assets | Where-Object {
    $_.name -match 'windows' -or $_.name -match 'pc-windows' -or $_.name -match '\.exe$'
} | Select-Object -First 1

if (-not $asset) {
    Write-Error "No Windows asset found in release '$($rel.tag_name)'. Check https://github.com/rtk-ai/rtk/releases and download manually into $dest."
    exit 1
}

$out = Join-Path $dest $asset.name
Write-Host "Downloading $($asset.name) ($($rel.tag_name))..."
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $out -Headers @{ 'User-Agent' = 'rtk-local-install' }

if ($out -match '\.zip$') {
    Expand-Archive -Path $out -DestinationPath $dest -Force
    Remove-Item $out
}

$exe = Get-ChildItem -Path $dest -Filter 'rtk*.exe' -Recurse | Select-Object -First 1
if ($exe) {
    Write-Host "RTK installed locally at: $($exe.FullName)"
    & $exe.FullName --version
} else {
    Write-Warning "Downloaded to $dest but no rtk*.exe found. Inspect the contents manually."
}
