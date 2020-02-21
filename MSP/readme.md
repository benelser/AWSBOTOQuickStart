# Metasploit Pro
Quick start on getting MSP up and running

## Step 1: Download Installer
Windows: [64-Bit](https://downloads.metasploit.com/data/releases/metasploit-latest-windows-installer.exe)
<br />
Linux: [64-Bit](https://downloads.metasploit.com/data/releases/metasploit-latest-linux-x64-installer.run)

## STEP 2: Install
Metasploit uses some of the same techniques as malware and malicious attackers to audit your security. For Metasploit to run properly, you must switch off anti-virus solutions and your local firewall before the installation and during its use. If you are not comfortable turning off defenses on this computer, consider installing Metasploit on a dedicated virtual machine (set virtual machine NIC to bridged mode). Ubuntu works great and doesn't incur any OS licensing fees.

Once the download is complete, run the installer and follow the step by step instructions. This installer contains all Metasploit editions.

## STEP 3 or sometime: Activate
*Get-LicenseKey*

## Step 4: Restart Service
```bash
/opt/metasploit/ctlscript.sh restart
```

## Check service is listening
```bash
netstat -anop | grep 3790
```

## Setup ssh tunnel with local port forward to access web front end
```bash
ssh -L 3790:localhost:3790 -N -f ec2-user@PublicDNS -i key_pairs.pem
```
### Browse to:
https://localhost:3790