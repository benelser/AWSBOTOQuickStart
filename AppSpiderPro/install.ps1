<powershell>
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
$url = "https://raw.githubusercontent.com/benelser/AWSBOTOQuickStart/master/AppSpiderPro/installer.ps1"
$output = "C:\Windows\Temp\installer.ps1"
$WebClient= New-Object net.webclient
$script = $WebClient.DownloadString($url)
$script > $output
#$command = Get-Content $output
$bytes = [System.Text.Encoding]::Unicode.GetBytes($script)
$encodedCommand = [Convert]::ToBase64String($bytes)
powershell.exe -encodedCommand $encodedCommand
</powershell>