#! /usr/bin/bash

export PATH=$PATH:/usr/local/mysql/bin
PASSWORD=$1
SLAVE1=$2
SLAVE2=$3


# cnf file

cat << EOF > /usr/local/mysql/my.cnf
[mysqld]
user=mysql
port=3306
basedir=/usr/local/mysql
datadir=/usr/local/mysql/data
socket=/tmp/mysql.sock
log-error=/usr/local/mysql/data/mysql_error.log
pid-file=/usr/local/mysql/bin/mysqld.pid
log-bin=/usr/local/mysql/data/mysql-bin
server-id=1
gtid-mode=ON
enforce-gtid-consistency=ON
log_replica_updates=ON

[client]
port=3306
socket=/tmp/mysql.sock
EOF

# service file

cat << EOF > /usr/lib/systemd/system/mysql.service
[Unit]

Description=MySQL Community Server

After=network.target

After=syslog.target



[Install]

WantedBy=multi-user.target

Alias=mysql.service


[Service]

User=mysql

Group=dba

# Start main service

ExecStart=/usr/local/mysql/bin/mysqld_safe --skip-grant-tables


# Give up if ping don't get an answer

TimeoutSec=300

PrivateTmp=false
EOF

# initialization
cd /usr/local/mysql/bin
./mysqld --defaults-file=/usr/local/mysql/my.cnf --initialize --user=mysql

echo "finished initialization"

cat /usr/local/mysql/data/mysql_error.log | grep "A temporary password is generated for root@localhost"

ROOTPASSWORD=$(cat /usr/local/mysql/data/mysql_error.log | grep "A temporary password is generated for root@localhost" | awk '{print $NF}')
echo "$ROOTPASSWORD"

trap "echo 'Command interrupted, but process continues.'" SIGINT

# exec
cd /usr/local/mysql/bin
./mysqld_safe
COMMAND_PID=$!
echo "$COMMAND_PID"

sleep 5
kill -SIGINT $COMMAND_PID


echo "alter user 'root'@localhost' identified by '$PASSWORD';" | mysql -u root -p'$ROOTPASSWORD'
echo "create database test;" | mysql -u root -p'$PASSWORD';
echo "create table test.test( userID varchar(20));" | mysql -u root -p'$PASSWORD'
echo "create user 'repl'@'%' identified by "$PASSWORD;" | mysql -u root -p'$PASSWORD'
echo "grant replication slave on *.* to 'repl'@'%';" | mysql -u root -p'$PASSWORD'
echo "flush privileges;" | mysql -u root -p'$PASSWORD'


# make dump file
cd /usr/local/mysql/bin
./mysqldump -u 'repl' -p test > test.sql

# send dump file to slave server
cd /usr/local/mysql/bin
scp test.sql 'root'@'$SLAVE1':/root/
scp test.sql 'root'@'$SLAVE2':/root/

echo "finished master DB setting"
