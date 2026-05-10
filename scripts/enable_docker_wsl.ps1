$ErrorActionPreference = "Stop"

Start-Transcript -Path "$env:TEMP\enable_docker_wsl.log" -Force | Out-Null

Write-Host "Enabling Windows features required by Docker Desktop WSL2 backend..."
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
dism.exe /online /enable-feature /featurename:HypervisorPlatform /all /norestart

Write-Host "Enabling Windows hypervisor at boot..."
bcdedit /set hypervisorlaunchtype auto

Write-Host "Updating WSL kernel/components if supported..."
wsl --update
wsl --set-default-version 2

Write-Host "Done. Reboot Windows before starting Docker Desktop again."
Stop-Transcript | Out-Null
