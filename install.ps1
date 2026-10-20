# Windows Installer for gads-ai-bridge
param(
    [string]$DeveloperToken = "",
    [string]$MccId = ""
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Installing gads-ai-bridge (Windows)     " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Check Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[ERROR] Python is not installed or not in PATH." -ForegroundColor Red
    exit 1
}
Write-Host "[+] Found Python: $($pythonCmd.Source)" -ForegroundColor Green

# 2. Install dependencies
Write-Host "[*] Installing dependencies..." -ForegroundColor Yellow
python -m pip install -r "$PSScriptRoot\requirements.txt" --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install dependencies." -ForegroundColor Red
    exit 1
}
Write-Host "[+] Dependencies installed successfully." -ForegroundColor Green

# 3. Create ~/.gads directory
$gadsHome = "$HOME\.gads"
$gadsBin = "$gadsHome\bin"
New-Item -ItemType Directory -Path $gadsHome -Force | Out-Null
New-Item -ItemType Directory -Path $gadsBin -Force | Out-Null

Copy-Item "$PSScriptRoot\src\gads_ai\cli.py" -Destination "$gadsHome\gads_tool.py" -Force

"@echo off`r`npython `"$gadsHome\gads_tool.py`" %*" | Set-Content "$gadsBin\gads.cmd" -Force
"& python `"$gadsHome\gads_tool.py`" `$args" | Set-Content "$gadsBin\gads.ps1" -Force

# 4. Handle credentials
if (Test-Path "$HOME\.gdoc\credentials.json") {
    Copy-Item "$HOME\.gdoc\credentials.json" -Destination "$gadsHome\credentials.json" -Force
    Write-Host "[+] Reused existing credentials from ~/.gdoc" -ForegroundColor Green
}

# 5. Handle Developer Token
if ($DeveloperToken) {
    & python "$gadsHome\gads_tool.py" config --developer-token $DeveloperToken
}

# 6. Add to User PATH
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath -notlike "*$gadsBin*") {
    $newUserPath = $userPath.TrimEnd(';') + ";$gadsBin"
    [Environment]::SetEnvironmentVariable("PATH", $newUserPath, "User")
    Write-Host "[+] Added $gadsBin to permanent User PATH." -ForegroundColor Green
} else {
    Write-Host "[+] $gadsBin is already in User PATH." -ForegroundColor Green
}

$env:PATH = "$env:PATH;$gadsBin"

Write-Host "`n[+] Installation complete!" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Enable Google Ads API in your Google Cloud project"
Write-Host "2. Run: gads config --developer-token <YOUR_TOKEN>"
Write-Host "3. Run: gads auth"
