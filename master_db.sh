#! /usr/bin/bash

PASSWORD=$1
SLAVE1=$2
SLAVE2=$3

QUREY="mysql -u root -p$PASSWORD"

# setting env
echo "export PATH=$PATH:/usr/local/mysql/bin" >> ~/.bash_profile
source ~/.bash_profile

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
log_slave_updates=ON
authentication_policy=mysql_native_password

[client]
port=3306
socket=/tmp/mysql.sock
EOF

# initialization
cd /usr/local/mysql/bin
./mysqld --defaults-file=/usr/local/mysql/my.cnf --initialize --user=mysql

echo "finished initialization"

# exec
cd ./usr/local/mysql/bin
./mysqld_safe &

mysql -u root -p$PASSWORD

$QUERY -e "create database test;"
$QUERY -e "use test;"
$QUERY -e "create table table1( userID varchar(20));" test
$QUERY -e "alter user 'repl'@'%' identified by '$PASSWORD';" test
$QUERY -e "grant replication slave on *.* to 'repl'@'%';"
$QUERY -e "flush privileges;"

# make dump file
cd /usr/local/mysql/bin
./mysqldump -u 'repl' -p test < test.sql

# send dump file to slave server
scp test.sql 'root'@'$SLAVE1':/root/
scp test.sql 'root'@'$SLAVE2':/root/

