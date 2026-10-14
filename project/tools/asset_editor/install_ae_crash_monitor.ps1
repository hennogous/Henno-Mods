# Install for the current desktop user, then start immediately.
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$taskName = 'CSC Asset Editor Crash Capture'
$installed = "$env:USERPROFILE\Desktop\Codex\Tools\AE Crash Capture"
$output = "$env:USERPROFILE\Desktop\Codex\AE_Crash_Captures"
$description = 'CSC AE diagnostics: hidden per-user ProcDump supervisor; full native crash dumps and AE logs; re-arms after each session.'
$old = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($old -and $old.Description -ne $description) { throw "An unrelated task already uses the name $taskName." }
New-Item -ItemType Directory -Path $installed -Force | Out-Null
foreach ($file in @('capture_ae_crash.ps1', 'watch_ae_crashes.ps1', 'watch_ae_assertions.ps1')) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot $file) -Destination $installed -Force
}
$identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$executable = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$arguments = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + (Join-Path $installed 'watch_ae_crashes.ps1') + '"'
$action = New-ScheduledTaskAction -Execute $executable -Argument $arguments
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $identity
$principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -Hidden -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName $taskName -Description $description -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
$assertTaskName = 'CSC Asset Editor Assertion Capture'
$assertDescription = 'CSC AE diagnostics: hidden per-user assertion snapshot monitor; no window interaction.'
$oldAssertionTask = Get-ScheduledTask -TaskName $assertTaskName -ErrorAction SilentlyContinue
if ($oldAssertionTask -and $oldAssertionTask.Description -ne $assertDescription) { throw "An unrelated task already uses the name $assertTaskName." }
$assertArguments = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + (Join-Path $installed 'watch_ae_assertions.ps1') + '"'
$assertAction = New-ScheduledTaskAction -Execute $executable -Argument $assertArguments
Register-ScheduledTask -TaskName $assertTaskName -Description $assertDescription -Action $assertAction -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $assertTaskName
Write-Output "Installed and started: $taskName"
Write-Output "Installed and started: $assertTaskName"
Write-Output "Evidence folder: $output"
