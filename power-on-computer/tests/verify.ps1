$ErrorActionPreference = 'Stop'
$skillRoot = Split-Path $PSScriptRoot -Parent
$skillFile = Join-Path $skillRoot 'SKILL.md'
$scriptFile = Join-Path $skillRoot 'scripts\power_on.ps1'
$exampleConfigFile = Join-Path $skillRoot 'config.example.json'

foreach ($file in @($skillFile, $scriptFile, $exampleConfigFile)) {
  if (-not (Test-Path -LiteralPath $file)) {
    throw "Missing required skill file: $file"
  }
}

$tempConfig = Join-Path ([System.IO.Path]::GetTempPath()) ("power-on-computer-verify-{0}.json" -f [guid]::NewGuid())
@{
  endpoint = 'http://apis.bemfa.com/va/sendMessage'
  uid = '00000000000000000000000000000000'
  topic = 'computerPower'
  type = '1'
  message = 'on'
} | ConvertTo-Json | Set-Content -LiteralPath $tempConfig -Encoding UTF8

try {
  $result = & $scriptFile -DryRun -ConfigPath $tempConfig | ConvertFrom-Json
} finally {
  Remove-Item -LiteralPath $tempConfig -Force -ErrorAction SilentlyContinue
}

if ($result.method -ne 'GET') { throw 'Expected a GET request' }
if ($result.host -ne 'apis.bemfa.com') { throw 'Unexpected API host' }
if ($result.topic -ne 'computerPower') { throw 'Unexpected MQTT topic' }
if ($result.type -ne '1') { throw 'Unexpected message type' }
if ($result.msg -ne 'on') { throw 'Unexpected MQTT message' }
if ($result.sent -ne $false) { throw 'DryRun must not send the request' }

Write-Host 'PASS: skill structure and non-mutating request contract verified.'
