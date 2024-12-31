#! /usr/bin/bash

SERVERID=$1
HOST=$2
PASSWORD=$3
MYSQLPORT=$4

QUERY="mysql -u root -p$PASSWORD"

# cnf file
echo '[mysqld]
user=mysql
port=3306
basedir=/usr/local/mysql
datadir=/usr/local/mysql/data
socket=/tmp/mysql.sock
log-error=/usr/local/mysql/data/mysql_error.log
pid-file=/usr/local/mysql/bin/mysqld.pid
log-bin=/usr/local/mysql/data/mysql-bin
server-id=$SERVERID
gtid-mode=ON
enforce-gtid-consistency=ON
log_slave_updates=ON
authentication_policy=mysql_native_password
read_only=1

[client]
port=3306
socket=/tmp/mysql.sock' /usr/local/mysql/my.cnf

# initialization
cd /usr/local/mysql/bin
./mysqld --defaults-file=/usr/local/mysql/my.cnf --initialize --user=mysql

# exec
cd /usr/local/mysql/bin
./mysqld_safe &

$QUERY test < /root/test.sql

$QUERY "CHANGE MASTER HOST='$HOST', MASTER_PORT=$MYSQLPORT, MASTER_USER='repl', MASTER_PASSWORD='$PASSWORD', MASTER_AUTO_POSITION=1,GET_MASTER_PUBLIC_KEY=1;"
