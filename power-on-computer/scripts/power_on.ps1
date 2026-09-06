param(
  [switch]$DryRun,
  [string]$ConfigPath
)

$ErrorActionPreference = 'Stop'
$skillRoot = Split-Path $PSScriptRoot -Parent
$defaultConfigPath = Join-Path $skillRoot 'config.json'
if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
  $ConfigPath = if (-not [string]::IsNullOrWhiteSpace($env:BEMFA_CONFIG)) { $env:BEMFA_CONFIG } else { $defaultConfigPath }
}

if (-not (Test-Path -LiteralPath $ConfigPath)) {
  throw "Bemfa configuration is missing: $ConfigPath"
}

$config = Get-Content -Raw -LiteralPath $ConfigPath | ConvertFrom-Json
$uid = [string]$config.uid
if ($uid -notmatch '^[a-fA-F0-9]{32}$') {
  throw 'Bemfa UID is missing or invalid.'
}

$endpoint = if (-not [string]::IsNullOrWhiteSpace([string]$config.endpoint)) { [string]$config.endpoint } else { 'http://apis.bemfa.com/va/sendMessage' }
$endpointUri = [uri]$endpoint
if ($endpointUri.Host -ne 'apis.bemfa.com' -or $endpointUri.Scheme -notin @('http', 'https')) {
  throw 'Bemfa endpoint must use http(s)://apis.bemfa.com.'
}

$topic = if (-not [string]::IsNullOrWhiteSpace([string]$config.topic)) { [string]$config.topic } else { 'computerPower' }
$type = if (-not [string]::IsNullOrWhiteSpace([string]$config.type)) { [string]$config.type } else { '1' }
$message = if (-not [string]::IsNullOrWhiteSpace([string]$config.message)) { [string]$config.message } else { 'on' }
$query = 'uid={0}&topic={1}&type={2}&msg={3}' -f @(
  [uri]::EscapeDataString($uid),
  [uri]::EscapeDataString($topic),
  [uri]::EscapeDataString($type),
  [uri]::EscapeDataString($message)
)
$uri = [uri]::new(('{0}?{1}' -f $endpoint, $query))

if ($DryRun) {
  [pscustomobject]@{
    sent = $false
    method = 'GET'
    host = $uri.Host
    topic = $topic
    type = $type
    msg = $message
  } | ConvertTo-Json -Compress
  exit 0
}

$response = Invoke-WebRequest -Uri $uri -Method Get -TimeoutSec 10 -UseBasicParsing
if ($response.StatusCode -lt 200 -or $response.StatusCode -ge 300) {
  throw "Bemfa returned HTTP status $($response.StatusCode)."
}

$apiResult = $null
try {
  $apiResult = $response.Content | ConvertFrom-Json
} catch {
  throw 'Bemfa returned a non-JSON response; command state is uncertain.'
}

if ($null -ne $apiResult.code -and [string]$apiResult.code -ne '0') {
  throw "Bemfa rejected the command: code=$($apiResult.code)."
}

[pscustomobject]@{
  sent = $true
  accepted = $true
  topic = $topic
  msg = $message
} | ConvertTo-Json -Compress
