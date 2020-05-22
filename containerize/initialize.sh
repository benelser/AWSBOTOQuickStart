#!/bin/bash

NXP_ROOT="/opt/rapid7/nexpose"
cd $NXP_ROOT/nsc
$NXP_ROOT/nsc/nsc.sh >/dev/null 2>&1 </dev/null &

status_file=/work/r7-status
if [ -f ${status_file} ]; then
  exit 0
fi

R7_INIT_PWD=chaNGEmeN0w
LICENSE_API=https://localhost:3780/api/3/administration/license
USER_API=https://localhost:3780/api/3/users/1
CMD_API=https://localhost:3780/api/3/administration/commands

r7pwd=${R7_INIT_PWD}
R7_PWD=blablalblablanope
R7_USER=r7user

echo "Attempt to set license info"
status=$(curl -k ${LICENSE_API} -u ${R7_USER}:${r7pwd} | grep status | cut -d':' -f2)
echo "${status}"

initial=0
while [[ ! ${status} =~ .*"Activated".* ]]
do
  echo "Sleeping ${initial}"
  sleep 60s
  ## if unauthoried...switch password
  if [[ ${status} =~ .*401,.* ]]
  then
    echo "Swapping password"
    r7pwd=${R7_PWD}
    initial=1
	fi
  if [[ ${status} =~ .*"Unlicensed".* ]]
  then
    echo "Posting new license"
    curl -k -X POST ${LICENSE_API} -u ${R7_USER}:${r7pwd} -F "license=@/work/license.lic"
  fi
  status=$(curl -k ${LICENSE_API} -u ${R7_USER}:${r7pwd} | grep status | cut -d':' -f2)
  echo "License status => [${status}]"
done

## update new password
if [[ ${initial} == 0 ]]
then
  echo "Updated user"
  curl -k -u ${R7_USER}:${R7_INIT_PWD} -X PUT ${USER_API} \
   --header "Content-Type: application/json" \
    --data '{"login":"'"${R7_USER}"'", "password": "'"${R7_PWD}"'", "name":"R7 User", "email": "r7@localhost.com", "role": {"allAssetGroups" : true,"allSites" : true,"id" : "global-admin","name" : "Global Administrator","superuser":true}}'
fi

## pull update if needed
curl -k -u ${R7_USER}:${R7_PWD} -X POST ${CMD_API} \
   --header "Content-Type: application/json" \
   --data "update now"

## send updates to scan engines
curl -k -u ${R7_USER}:${R7_PWD} -X POST ${CMD_API} \
   --header "Content-Type: application/json" \
   --data "update engines"

rm -rf /work/license.lic

echo "R7 is ready" > ${status_file}