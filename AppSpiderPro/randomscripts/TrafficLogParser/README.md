# Parse AppSpider Traffic Log
This was created because I am a flawed human being. I do not carry sed,awk,grep, or regex in my head, I'm sorry. I built this for if the time should arise and I need it. If you find use out of go for it. 

Tested on:
```bash
PSVersion                      7.0.1
PSEdition                      Core
GitCommitId                    7.0.1
OS                             Darwin 19.4.0 Darwin Kernel Version 19.4.0: Wed Mar  4 22:28:40 PST 2…
Platform                       Unix
PSCompatibleVersions           {1.0, 2.0, 3.0, 4.0…}
PSRemotingProtocolVersion      2.3
SerializationVersion           1.1.0.1
WSManStackVersion              3.0
```

Example usage:
```powershell
# Parses log and creates AttackTraffic objects for each engine --> server exchange
$traffic = Get-AttackTraffic -Path "/Users/belser/Downloads/logparser/traffic_00000.log"

## Get Post request cookies
$traffic | Where-Object {$_.Request.Method -eq "Post"} | Select-Object {$_.Request.Headers["user-agent"]}
$traffic | Where-Object {$_.Request.Method -eq "Post"} | Select-Object {$_.Request.Headers["cookie"]}

# Get specific exchange
$55 = $traffic | Where-Object {$_.Detail.Index -eq 55}
```