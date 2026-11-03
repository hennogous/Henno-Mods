param([Parameter(Mandatory=$true)][string]$OutputRoot)
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath $OutputRoot){throw 'Use a fresh test output directory.'}
$sessionRoot=Join-Path $OutputRoot 'sessions'
New-Item -ItemType Directory -Path $sessionRoot -Force | Out-Null
$checks=0
function Assert-Check([bool]$Condition,[string]$Message){if(-not $Condition){throw $Message};$script:checks++}
function New-Fixture([string]$Id,[bool]$Old=$true,[bool]$Project=$true){
    $folder=Join-Path $sessionRoot $Id
    New-Item -ItemType Directory -Path $folder -Force | Out-Null
    if($Project){
        New-Item -ItemType Directory -Path (Join-Path $folder 'project\CSC_Native_AI.rep') -Force | Out-Null
        'fixture' | Set-Content -LiteralPath (Join-Path $folder 'project\CSC_Native_AI.gpr')
        'disposable' | Set-Content -LiteralPath (Join-Path $folder 'project\CSC_Native_AI.rep\db.gbf')
    }
    if($Old){[IO.Directory]::SetCreationTimeUtc($folder,[DateTime]::UtcNow.AddHours(-4))}
    return $folder
}
$old=New-Fixture ('1'*32)
$active=New-Fixture ('2'*32)
$fresh=New-Fixture ('3'*32) $false
$unknown=New-Fixture ('4'*32) $true $false
$named=New-Fixture 'master-project'
$master=Join-Path $OutputRoot 'project'
New-Item -ItemType Directory -Path $master | Out-Null
'canonical' | Set-Content -LiteralPath (Join-Path $master 'master.gbf')
function Get-CimInstance { param($ClassName,$ErrorAction) [pscustomobject]@{Name='python.exe';CommandLine=('python launcher.py --worker "'+$active+'"');ProcessId=12345} }
$cleaner=Join-Path $PSScriptRoot 'cleanup_ghidra_sessions.ps1'
$preview=& $cleaner -SessionRoot $sessionRoot | ConvertFrom-Json
Assert-Check ($preview.Candidates -eq 1) 'Only inactive old project copy should qualify.'
Assert-Check ($preview.ActivePreserved -eq 1) 'Live worker must be recognized.'
Assert-Check (Test-Path -LiteralPath $old) 'Preview must not delete.'
$result=& $cleaner -SessionRoot $sessionRoot -Apply -ReceiptDirectory (Join-Path $OutputRoot 'receipts') | ConvertFrom-Json
Assert-Check ($result.RemovedSessions -eq 1) 'One disposable session must be removed.'
Assert-Check (-not (Test-Path -LiteralPath $old)) 'Old inactive session must be gone.'
foreach($path in @($active,$fresh,$unknown,$named,$master)){Assert-Check (Test-Path -LiteralPath $path) "Protected directory removed: $path"}
$receipt=Get-Content -LiteralPath $result.Receipt -Raw | ConvertFrom-Json
Assert-Check ($receipt.RemovedBytes -gt 0) 'Actual removal size must be recorded.'
Assert-Check $receipt.Entries[0].Removed 'Per-session removal receipt must confirm success.'
$queryFailure=New-Fixture ('5'*32)
function Get-CimInstance {param($ClassName,$ErrorAction) throw 'Simulated process query failure'}
$rejected=$false
try{& $cleaner -SessionRoot $sessionRoot -Apply -Quiet}catch{$rejected=$true}
Assert-Check $rejected 'Failed process query must stop cleanup.'
Assert-Check (Test-Path -LiteralPath $queryFailure) 'Query failure must preserve all candidates.'
[pscustomobject]@{Passed=$true;Checks=$checks} | ConvertTo-Json | Tee-Object -FilePath (Join-Path $OutputRoot 'result.json')
