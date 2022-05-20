#! /bin/bash

# sh setup_client_node.sh 155.98.39.143

server=$1

sudo apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8
sudo add-apt-repository 'deb [arch=amd64] http://nyc2.mirrors.digitalocean.com/mariadb/repo/10.4/ubuntu bionic main'
sudo apt update
sudo apt install mariadb-client
