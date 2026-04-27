$ErrorActionPreference = 'Stop'

$cargo = Get-Command cargo -ErrorAction SilentlyContinue
if (-not $cargo) {
    throw "cargo not found in PATH. The rust-ms dependency should have provided it. Try: choco install rust-ms -y"
}

Write-Host "Installing tokenmix-cli from crates.io..."
& cargo install tokenmix-cli
if ($LASTEXITCODE -ne 0) {
    throw "cargo install failed with exit code $LASTEXITCODE"
}

Write-Host ""
Write-Host "tokenmix-cli installed."
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Get a free API key at https://tokenmix.ai"
Write-Host "  2. `$env:TOKENMIX_API_KEY = 'tm-your_key_here'"
Write-Host "  3. tokenmix chat 'Hello'"
