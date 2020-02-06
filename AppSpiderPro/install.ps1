$uri = "http://download2.rapid7.com/download/AppSpider/AppSpiderFullSetup.exe"
$desktop = "$env:USERPROFILE\Desktop"
$asp = "$desktop\AppSpiderFullSetup.exe"
Invoke-WebRequest -Uri $uri -OutFile $asp
& $asp /S install /UI /CMD