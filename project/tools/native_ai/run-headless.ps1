param(
 [Parameter(Mandatory=$true)][string]$AnalysisRoot,
 [Parameter(Mandatory=$true)][string]$GhidraHome,
 [Parameter(Mandatory=$true)][string]$JavaHome,
 [Parameter(Mandatory=$true)][string]$Targets,
 [Parameter(Mandatory=$true)][string]$Mapping,
 [string]$ProjectName='CSC_Native_AI',
 [string]$Program='GameCore_XP2_FinalRelease.dll',
 [string]$Output='exports',
 [string]$ImportBinary
)
$ErrorActionPreference='Stop'
$r=[IO.Path]::GetFullPath($AnalysisRoot)
$env:JAVA_HOME=[IO.Path]::GetFullPath($JavaHome)
$env:_JAVA_OPTIONS="-Dapplication.settingsdir=$r\ghidra-settings -Dapplication.cachedir=$r\ghidra-cache -Dapplication.tempdir=$r\ghidra-temp"
New-Item -ItemType Directory -Force -Path (Join-Path $r $Output),(Join-Path $r 'ghidra-project')|Out-Null
$argsList=@((Join-Path $r 'ghidra-project'),$ProjectName)
if($ImportBinary){$argsList+=@('-import',[IO.Path]::GetFullPath($ImportBinary),'-analysisTimeoutPerFile','1200','-max-cpu','4')}
else{$argsList+=@('-process',$Program,'-noanalysis')}
$argsList+=@('-scriptPath',$PSScriptRoot,'-postScript','ExportAiTargets.java',(Join-Path $r $Output),[IO.Path]::GetFullPath($Targets),[IO.Path]::GetFullPath($Mapping),'-log',(Join-Path $r 'ghidra-analysis.log'),'-scriptlog',(Join-Path $r 'ghidra-scripts.log'))
& (Join-Path $GhidraHome 'support/analyzeHeadless.bat') @argsList
exit $LASTEXITCODE
