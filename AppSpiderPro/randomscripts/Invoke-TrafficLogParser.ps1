using namespace System
using namespace System.IO
using namespace System.Text
using namespace System.Collections

class Details {
    [int]$Index
    [string]$Time
    [int]$ResponseTimeMS
    [int]$ResponseCode
    [bool]$Failed
}

class Request {
    [string]$Method
    [string]$URL
    [Hashtable]$Headers
    [string]$RequestBody
}

class Response {
    [int]$ResponseCode
    [ArrayList]$headers
    [string]$ResponseBody
}

class AttackTraffic {
    [Details]$Detail
    [Request]$Request
    [Response]$Response
    AttackTraffic($d, $req, $res) {
        $this.Detail = $d
        $this.Request = $req
        $this.Response = $res
    }
}
function Read-Detail {
    param (
        [StreamReader]$sr
    )
    
    $details = [Details]::new()
    for ($i = 0; $i -lt 5; $i++) {
        $line = $sr.ReadLine()
        if ([string]::IsNullOrWhiteSpace($line) -or $sr.EndOfStream -eq $true) {
            continue
        }
        switch ($i) {
            0 { $details.Index = $line.Split(":")[1].Trim() }
            1 { $details.Time = $line.Split(":")[1].Trim() }
            2 { $details.ResponseTimeMS = $line.Split(":")[1].Trim().Split("m")[0]}
            3 { $details.ResponseCode = $line.Split(":")[1].Trim() }
            4 { 
                $failed = $line.Split(":")[1].Trim() 
                if ($failed -eq "No") {
                    $details.Failed = $false
                }
                else {
                    $details.Failed = $true
                }
            }
            Default {}
        }
    }
    [PSCustomObject]$returnObject = @{
        Details = $details
        Position = "============= Request ==================="
    }
    return $returnObject
}
function Read-Request {
    param (
        [StreamReader]$sr
    )
    $line = $sr.ReadLine()
    while($line -ne "============= Request ===================" -or $sr.EndOfStream -eq $true) {
        $line = $sr.ReadLine()
        continue
    }
    $line = $sr.ReadLine()
    $request = [Request]::new()
    $request.Method = $line.Split(" ")[0].Trim()
    $request.URL = $line.Split(" ")[1].Trim()
    $headers = @{}
    while($true) {
        $line = $sr.ReadLine()
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }
        if ($line -eq "============= Response ===================" -or $sr.EndOfStream -eq $true) {
            $request.Headers = $headers
            [PSCustomObject]$returnObject = @{
                Request = $request
                Position = "============= Response ==================="
            }
            return $returnObject
        
        }
        $key = $line.Split(":")[0].Trim()
        try {
            $value = $line.Split(":")[1].Trim()
        }
        catch {
            [Console]::WriteLine("No value when parsing`n$line")
        }
        $value = $null
        $headers.Add($key, $value) 
    }
    $request.Headers = $headers
    [PSCustomObject]$returnObject = @{
        Request = $request
        Position = "============= Response ==================="
    }
    return $returnObject

}

function Read-Request1 {
    param (
        [StreamReader]$sr
    )
    $line = $sr.ReadLine()
    while($line -ne "============= Request ===================" -or $sr.EndOfStream -eq $true) {
        $line = $sr.ReadLine()
        continue
    }
    $line = $sr.ReadLine()
    $request = [Request]::new()
    $request.Method = $line.Split(" ")[0].Trim()
    $request.URL = $line.Split(" ")[1].Trim()
    $headers = @{}
    do {
        $line = $sr.ReadLine()
        if ([string]::IsNullOrWhiteSpace($line) -or $sr.EndOfStream -eq $true) {
            $body = [StringBuilder]::new()
            while ($true) {
                $line = $sr.ReadLine()
                if ($line -eq "============= Response ===================" -or $sr.EndOfStream -eq $true) {
                    $request.RequestBody = $body.ToString()
                    $request.Headers = $headers
                    [PSCustomObject]$returnObject = @{
                        Request = $request
                        Position = "============= Response ==================="
                    }
                    return $returnObject
                }
                if ([string]::IsNullOrWhiteSpace($line)) {
                    continue
                }
                [void]$body.Append($line)
            }
            $request.RequestBody = $body.ToString()
            $request.Headers = $headers
            [PSCustomObject]$returnObject = @{
                Request = $request
                Position = "============= Details ==================="
            }
            return $returnObject
        }
        $headers.Add($line.Split(":")[0].Trim(), $line.Split(":")[1].Trim())
    } until ([string]::IsNullOrWhiteSpace($line) -or $sr.EndOfStream -eq $true)
    $request.RequestBody = $body.ToString()
    $request.Headers = $headers
    [PSCustomObject]$returnObject = @{
        Request = $request
        Position = "============= Details ==================="
    }
    return $returnObject

}
function Read-Response {
    param (
        [StreamReader]$sr
    )
    $line = $sr.ReadLine()
    $response = [Response]::new()
    $response.ResponseCode = $line.Split(" ")[1].Trim()
    [ArrayList]$headers = @()
    do {
        $line = $sr.ReadLine()
        if ([string]::IsNullOrWhiteSpace($line) -or $sr.EndOfStream -eq $true) {
            $body = [StringBuilder]::new()
            while ($true) {
                $line = $sr.ReadLine()
                if ($line -eq "============= Details ===================" -or $sr.EndOfStream -eq $true) {
                    $response.ResponseBody = $body.ToString()
                    $response.Headers = $headers
                    [PSCustomObject]$returnObject = @{
                        Response = $response
                        Position = "============= Details ==================="
                    }
                    return $returnObject
                }
                if ([string]::IsNullOrWhiteSpace($line)) {
                    continue
                }
                [void]$body.Append($line)
            }
            $response.ResponseBody = $body.ToString()
            $response.Headers = $headers
            [PSCustomObject]$returnObject = @{
                Response = $response
                Position = "============= Details ==================="
            }
            return $returnObject
        }
        $header = @{}
        $header.Add($line.Split(":")[0].Trim(), $line.Split(":")[1].Trim())
        [void]$headers.Add($header)
       
    } until ($line -eq "============= Details ===================" -or $sr.EndOfStream -eq $true)
    $response.ResponseBody = $body.ToString()
    $response.Headers = $headers
    [PSCustomObject]$returnObject = @{
        Response = $response
        Position = "============= Details ==================="
    }
    return $returnObject

}

function Get-AttackTraffic {
    param (
       [string]$Path  
    )
    if(!(Test-Path $Path)){
        Write-Error "Provide absolute path to log file.`nExample:`tGet-AttackTraffic -Path '/Users/test/mylog001.log'"
        exit
    }
    $log = [StreamReader]::new($Path)
    $line = $log.ReadLine()
    [ArrayList]$Conversations = @()
    $counter = 0
    $t = 0
    while ($log.EndOfStream -ne $true) {
        if ($counter -eq 3) {
            
            [void]$Conversations.Add([AttackTraffic]::new($details.Details, $request.Request, $response.Response))
            $counter = 0
        }
        if ([string]::IsNullOrWhiteSpace($line)) {
            $line = $log.ReadLine()
            continue
        }
        if ($line -eq "============= Details ===================") {
            $details = Read-Detail -sr $log
            $line = $details.Position
            $counter ++
            $t ++
            continue
        }
        if ($line -eq "============= Request ===================") {
            $request = Read-Request1 -sr $log
            $line = $request.Position
            $counter ++
            continue
            
        }
        if ($line -eq "============= Response ===================") {
            $response = Read-Response -sr $log
            $line = $response.Position
            $counter ++
            continue
        }

    }
    
    return $Conversations
}

# Parses log and creates AttackTraffic objects for each engine --> server exchange
$traffic = Get-AttackTraffic -Path "/Users/belser/Downloads/logparser/traffic_00000.log"

## Get Post request cookies
$traffic | Where-Object {$_.Request.Method -eq "Post"} | Select-Object {$_.Request.Headers["user-agent"]}
$traffic | Where-Object {$_.Request.Method -eq "Post"} | Select-Object {$_.Request.Headers["cookie"]}

# Get specific exchange
$55 = $traffic | Where-Object {$_.Detail.Index -eq 55}