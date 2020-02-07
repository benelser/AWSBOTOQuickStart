function InstallExe {
    
    $uri = "http://download2.rapid7.com/download/AppSpider/AppSpiderFullSetup.exe"
    $desktop = "$env:USERPROFILE\Desktop"
    $asp = "$desktop\AppSpiderFullSetup.exe"
    Invoke-WebRequest -Uri $uri -OutFile $asp
    & $asp /S install /UI /CMD
}

# Attempt to download installer
InstallExe
$attempts = 0
while (!(Get-Item "$desktop\install.log")) {

    if ($attempts -eq 3) {
        Restart-Computer
    }
    InstallExe
    $attempts ++
}

# Loop until program has been installed
while ($true)
{
    if((Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName | Where-Object {$_.DisplayName -like "*appspider*"}))
    {
        Restart-Computer -Force
    }
}