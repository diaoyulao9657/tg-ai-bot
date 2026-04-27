$ErrorActionPreference = 'Continue'
Write-Host "Uninstalling tokenmix-cli (cargo uninstall)..."
& cargo uninstall tokenmix-cli 2>$null
Write-Host "Done."
