#!/bin/bash
wget -c http://download2.rapid7.com/download/InsightVM/Rapid7Setup-Linux64.bin
chmod +x Rapid7Setup-Linux64.bin
./Rapid7Setup-Linux64.bin -q -Vfirstname=rapid -Vlastname=seven -Vcompany=r7 -Vusername=nxadmin -Vpassword1=ecadmin -Vpassword2=ecadmin
systemctl start nexposeconsole.service
init 6