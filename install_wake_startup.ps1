$ErrorActionPreference = "Stop"
$Project = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source
if (-not $Python) { $Python = (Get-Command python.exe -ErrorAction Stop).Source }
$Script = Join-Path $Project "jarvis_wake.py"
$Action = New-ScheduledTaskAction -Execute $Python -Argument "`"$Script`"" -WorkingDirectory $Project
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Days 0)
Register-ScheduledTask -TaskName "BalaJarvisWake" -Action $Action -Trigger $Trigger -Settings $Settings -Description "Starts the offline BALA JARVIS wake-word listener at sign-in." -Force | Out-Null
Write-Host "BALA JARVIS wake listener is configured to start at sign-in."
