#!/bin/bash
set -e

# 安装依赖包
os=$(cat /proc/version)
if (echo $os|grep centos)
then
    yum install -y epel-release
    yum install -y gcc smartmontools dmidecode python-pip python-devel
elif (echo $os|grep Ubuntu)
then
    apt-get install smartmontools dmidecode python-pip python-dev
else
    echo "your os version is not supported!"
fi


echo "####install pip mirror####"
mkdir -p  ~/.pip
cat <<EOF > ~/.pip/pip.conf
[global]
index-url = http://mirrors.aliyun.com/pypi/simple/

[install]
trusted-host=mirrors.aliyun.com
EOF

echo "####client prepare finished!###"
