# Windows Codex CLI. Run once with -Setup; subsequent runs need no key prompt.
[CmdletBinding(PositionalBinding=$false)]
param([switch]$Setup, [string]$Url = 'https://91.149.239.14:10443/mcp', [Parameter(ValueFromRemainingArguments=$true)][string[]]$CodexArguments)
$ErrorActionPreference = 'Stop'
$dir = Join-Path $env:LOCALAPPDATA 'PTB/harness'
$file = Join-Path $dir 'access.dpapi'
if ($Setup) {
    if (-not $Url -or ([uri]$Url).Scheme -ne 'https') { throw 'Specify the HTTPS MCP URL with -Url' }
    New-Item -ItemType Directory -Force $dir | Out-Null
    $secret = Read-Host 'PTB access key' -AsSecureString
    if ($secret.Length -ne 12) { throw 'Expected a 12-character access key' }
    codex mcp add ptb --url $Url --bearer-token-env-var PTB_ACCESS_KEY
    if ($LASTEXITCODE) { throw 'MCP registration failed' }
    ConvertFrom-SecureString $secret | Set-Content -LiteralPath $file
    return
}
$secret = ConvertTo-SecureString (Get-Content -LiteralPath $file -Raw).Trim()
try {
    $env:PTB_ACCESS_KEY = [System.Net.NetworkCredential]::new('', $secret).Password
    codex @CodexArguments
} finally {
    Remove-Item Env:PTB_ACCESS_KEY -ErrorAction SilentlyContinue
}
