#!/bin/bash

sudo apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8
sudo add-apt-repository 'deb [arch=amd64] http://nyc2.mirrors.digitalocean.com/mariadb/repo/10.4/ubuntu bionic main'
sudo apt update
sudo apt install mariadb-server

sudo mysql -uroot -e "set password = password("123456"); quit;"
sudo systemctl stop mysql
sudo systemctl status mysql

sudo systemctl start mysql

#grant access for client node, the ip 'root'@'%.emulab.net' need to be changed
sudo mysql -u root -p123456 -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%.emulab.net' IDENTIFIED BY '123456' WITH GRANT OPTION;"
