[CmdletBinding()]
param(
    [string]$VaultPath,
    [string]$EvalPath,
    [string]$HoldoutPath
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
$defaultEvalPath = Join-Path $skillPath 'evals\evals.json'
$defaultHoldoutPath = Join-Path $skillPath 'evals\holdout.json'
$evalFile = if ($EvalPath) { $EvalPath } else { $defaultEvalPath }
$holdoutFile = if ($HoldoutPath) { $HoldoutPath } else { $defaultHoldoutPath }

Assert-Condition (Test-Path -LiteralPath $skillFile -PathType Leaf) 'SKILL.md is missing'
Assert-Condition (Test-Path -LiteralPath $uiFile -PathType Leaf) 'agents/openai.yaml is missing'
Assert-Condition (Test-Path -LiteralPath $evalFile -PathType Leaf) 'training eval file is missing'
Assert-Condition (Test-Path -LiteralPath $holdoutFile -PathType Leaf) 'holdout eval file is missing'

$skillText = Get-Content -LiteralPath $skillFile -Raw
Assert-Condition ($skillText -match '(?s)^---\r?\nname:\s*[^\r\n]+\r?\ndescription:\s*[^\r\n]+\r?\n---') 'SKILL.md frontmatter is invalid'

$requiredHeadings = @(
    '## CLI-first rule',
    '## Read-only and scope boundaries',
    "## Read the vault's own rules first",
    '## Shared note safety',
    '## Read the relevant reference by task',
    '## Multiple vaults',
    '## Completion criteria'
)

foreach ($heading in $requiredHeadings) {
    Assert-Condition $skillText.Contains($heading) "Missing required section: $heading"
}

$requiredReferences = @(
    'references/workflows.md',
    'references/note-organization.md',
    'references/git-delivery.md'
)

foreach ($reference in $requiredReferences) {
    $referencePath = Join-Path $skillPath $reference
    Assert-Condition (Test-Path -LiteralPath $referencePath -PathType Leaf) "Missing reference: $reference"
    Assert-Condition $skillText.Contains($reference) "SKILL.md does not point to: $reference"
}

Assert-Condition (-not $skillText.Contains('### Capture and creation')) 'Detailed creation workflow leaked back into SKILL.md'
Assert-Condition (-not $skillText.Contains('### Archiving')) 'Detailed archive workflow leaked back into SKILL.md'
Assert-Condition (-not $skillText.Contains('### Review')) 'Detailed review workflow leaked back into SKILL.md'
Assert-Condition ($skillText.Contains('property:set')) 'Write-command safety boundary is missing'
Assert-Condition ($skillText.Contains('private or excluded paths')) 'Private-path safety boundary is missing'

function Read-EvalSet {
    param([string]$Path, [string]$ExpectedSplit)

    $data = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    Assert-Condition ($data.skill_name -eq 'obsidian-cli-knowledge-base') "$ExpectedSplit eval skill name is invalid"
    Assert-Condition ($data.baseline_commit -eq 'e4d4f36') "$ExpectedSplit eval baseline is not recorded"
    Assert-Condition ($data.evals.Count -gt 0) "$ExpectedSplit eval set is empty"

    foreach ($item in $data.evals) {
        Assert-Condition ($item.split -eq $ExpectedSplit) "$ExpectedSplit case has an invalid split"
        Assert-Condition (-not [string]::IsNullOrWhiteSpace($item.id)) "$ExpectedSplit case has no id"
        Assert-Condition (-not [string]::IsNullOrWhiteSpace($item.prompt)) "$ExpectedSplit case has no prompt"
        Assert-Condition (-not [string]::IsNullOrWhiteSpace($item.expected_route)) "$ExpectedSplit case has no expected route"
        Assert-Condition ($item.assertions.Count -gt 0) "$ExpectedSplit case has no assertions"
    }

    return $data
}

$train = Read-EvalSet -Path $evalFile -ExpectedSplit 'train'
$holdout = Read-EvalSet -Path $holdoutFile -ExpectedSplit 'holdout'
Assert-Condition ($train.evals.Count -ge 6) 'Training eval set must contain at least 6 cases'
Assert-Condition ($holdout.evals.Count -ge 3) 'Holdout eval set must contain at least 3 cases'

$allIds = @($train.evals.id) + @($holdout.evals.id)
Assert-Condition (($allIds | Sort-Object -Unique).Count -eq $allIds.Count) 'Eval ids must be unique across train and holdout'

if ($VaultPath) {
    Assert-Condition (Test-Path -LiteralPath $VaultPath -PathType Container) "Vault path does not exist: $VaultPath"

    $obsidian = Get-Command obsidian -ErrorAction SilentlyContinue
    Assert-Condition ($null -ne $obsidian) 'Obsidian CLI is not available on PATH'

    $reportedPath = (& $obsidian.Source vault info=path | Out-String).Trim()
    $expectedPath = (Resolve-Path -LiteralPath $VaultPath).Path
    $actualPath = (Resolve-Path -LiteralPath $reportedPath).Path
    Assert-Condition ($actualPath -eq $expectedPath) "Obsidian CLI target mismatch: $reportedPath"
}

Write-Output "PASS: skill structure, references, train ($($train.evals.Count)), holdout ($($holdout.evals.Count)), and configured vault checks passed"
