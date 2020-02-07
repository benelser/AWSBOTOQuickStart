function InstallExe {
    
    $uri = "http://download2.rapid7.com/download/AppSpider/AppSpiderFullSetup.exe"
    $desktop = "$env:USERPROFILE\Desktop"
    $asp = "$desktop\AppSpiderFullSetup.exe"
    Invoke-WebRequest -Uri $uri -OutFile $asp
    & $asp /S install /UI /CMD
}

$installerLog = "C:\Windows\Temp\installer.log"
Write-Output "Pid: " + $PID >> $installerLog
Write-Output "Top of first install attempt" >> $installerLog

# Attempt to download installer
InstallExe
$attempts = 0
while (!(Get-Item "$desktop\install.log")) {

    Write-Output "Looping waiting for install.log. Attempts: $attempts" >> $installerLog
    if ($attempts -eq 3) {
        Restart-Computer
    }
    InstallExe
    $attempts ++
}

$count = 0
# Loop until program has been installed
while ($true)
{
    Write-Output "Looping For isntall. Attempts: $count" >> $installerLog
    $count ++
    if((Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName | Where-Object {$_.DisplayName -like "*appspider*"}))
    {
        Write-Output "Restarting.." >> $installerLog
        Restart-Computer -Force
    }
}