#!/bin/bash

XMX_MEM=${XMX:-10g}
XMS_MEM=${XMS:-2g}

# modify the env file to fix r7's memory consumption from going nuts
sed -i "s/^-Xmx.*$/-Xmx${XMX_MEM}/" /opt/rapid7/nexpose/nsc/NeXposeEnvironment.env
sed -i "s/^-Xms.*$/-Xms${XMS_MEM}/" /opt/rapid7/nexpose/nsc/NeXposeEnvironment.env

NXP_ROOT="/opt/rapid7/nexpose"
cd $NXP_ROOT/nsc
$NXP_ROOT/nsc/nsc.sh