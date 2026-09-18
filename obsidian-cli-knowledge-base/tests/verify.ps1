[CmdletBinding()]
param(
    [string]$VaultPath
)

$ErrorActionPreference = 'Stop'

function Assert-Condition {
    param(
        [bool]$Condition,
        [string]$Message
    )

    if (-not $Condition) {
        throw "FAIL: $Message"
    }
}

$skillPath = Split-Path -Parent $PSScriptRoot
$skillFile = Join-Path $skillPath 'SKILL.md'
$uiFile = Join-Path $skillPath 'agents\openai.yaml'

Assert-Condition (Test-Path -LiteralPath $skillFile -PathType Leaf) 'SKILL.md is missing'
Assert-Condition (Test-Path -LiteralPath $uiFile -PathType Leaf) 'agents/openai.yaml is missing'

$skillText = Get-Content -LiteralPath $skillFile -Raw
Assert-Condition ($skillText -match '(?s)^---\r?\nname:\s*[^\r\n]+\r?\ndescription:\s*[^\r\n]+\r?\n---') 'SKILL.md frontmatter is invalid'

$requiredHeadings = @(
    '## CLI-first rule',
    '## Configurable Git completion policy',
    '## Read the vault''s own rules first',
    '## Writing discipline: link, don''t duplicate',
    '## Sub-folder grouping inside a topic',
    '## Standard workflows',
    '## Multiple vaults'
)

foreach ($heading in $requiredHeadings) {
    Assert-Condition $skillText.Contains($heading) "Missing required section: $heading"
}

if ($VaultPath) {
    Assert-Condition (Test-Path -LiteralPath $VaultPath -PathType Container) "Vault path does not exist: $VaultPath"

    $obsidian = Get-Command obsidian -ErrorAction SilentlyContinue
    Assert-Condition ($null -ne $obsidian) 'Obsidian CLI is not available on PATH'

    $reportedPath = (& $obsidian.Source vault info=path | Out-String).Trim()
    $expectedPath = (Resolve-Path -LiteralPath $VaultPath).Path
    $actualPath = (Resolve-Path -LiteralPath $reportedPath).Path
    Assert-Condition ($actualPath -eq $expectedPath) "Obsidian CLI target mismatch: $reportedPath"

    $unresolved = (& $obsidian.Source unresolved total | Out-String).Trim()
    Assert-Condition ($unresolved -eq '0') "Vault has unresolved links: $unresolved"
}

Write-Output 'PASS: skill structure and configured vault checks passed'
