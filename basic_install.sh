#! /usr/bin/bash

echo "start install db"

PASSWORD=$1
MYSQLPORT=$2


# make group
groupadd dba
useradd -g dba mysql

# download
wget https://dev.mysql.com/get/Downloads/MySQL-8.0/mysql-8.0.32-linux-glibc2.12-x86_64.tar.xz

# tar
tar -xvf mysql-8.0.32-linux-glibc2.12-x86_64.tar.xz 

# change file name
mv /root/mysql-8.0.32-linux-glibc2.12-x86_64 /usr/local/mysql
chown -R mysql.dba /usr/local/mysql
chmod 750 /usr/local/mysql

# make data file
mkdir /usr/local/mysql/data
chown -R mysql.dba /usr/local/mysql/data
chmod 750 /usr/local/mysql/data

# firewall
systemctl start firewalld
firewall-cmd --zone=public --permanent --add-port=$MYSQLPORT/tcp
firewall-cmd --reload


