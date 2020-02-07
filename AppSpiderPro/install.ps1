<powershell>
function InstallExe {
    
    $uri = "http://download2.rapid7.com/download/AppSpider/AppSpiderFullSetup.exe"
    $desktop = "$env:USERPROFILE\Desktop"
    $asp = "$desktop\AppSpiderFullSetup.exe"
    Invoke-WebRequest -Uri $uri -OutFile $asp
    & $asp /S install /UI /CMD
    Start-Sleep -Seconds 300
}

$installerLog = "C:\Windows\Temp\installer.log"
Write-Output "Pid: $PID" >> $installerLog

# Attempt to download installer
InstallExe
$attempts = 0
$desktop = "$env:USERPROFILE\Desktop"
while (!(Get-Item "$desktop\install.log")) {

    Write-Output "Install Attempts: $attempts" >> $installerLog
    if ($attempts -eq 2) {
        Write-Output "Something went wrong while attempting to install ASP" >> $installerLog
        Restart-Computer
    }
    InstallExe
    $attempts ++
}

# Loop until program has been installed
$count = 1
while ($true)
{
    Write-Output "Checking for install: $count" >> $installerLog
    $count ++
    Start-Sleep -Seconds 60
    if((Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName | Where-Object {$_.DisplayName -like "*appspider*"}))
    {
        Write-Output "Restarting.." >> $installerLog
        Restart-Computer -Force
    }
}
</powershell>