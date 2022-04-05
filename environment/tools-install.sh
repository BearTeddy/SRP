#!/bin/bash

VAGRANT_HOST_DIR=/mnt/host_machine

########################
# Node & npm
########################
echo "Installing Node & npm"
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt-get -y install nodejs
sudo apt-get -y install npm

########################
# Docker
########################
echo "Installing Docker"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt -y install docker-ce
sudo systemctl enable docker
sudo usermod -aG docker ${USER}
sudo usermod -aG docker jenkins

#docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

#git 
sudo apt-get install -y git

# MySQL install
# Download and Install the Latest Updates for the OS
sudo apt-get upgrade -y

# Set the Server Timezone to CST
echo "America/Chicago" > /etc/timezone
sudo dpkg-reconfigure -f noninteractive tzdata

# Enable Ubuntu Firewall and allow SSH & MySQL Ports
sudo ufw enable
sudo ufw allow 22
sudo ufw allow 3306

# Install essential packages
sudo apt-get -y install zsh htop
sudo apt-get install libssl-dev

# Install MySQL Server in a Non-Interactive mode. Default root password will be "root"
echo "mysql-server-5.6 mysql-server/root_password password root" | sudo debconf-set-selections
echo "mysql-server-5.6 mysql-server/root_password_again password root" | sudo debconf-set-selections
sudo apt-get -y install mariadb-server-10.5

sudo apt install pip
pip3 install flask
pip3 insall pysrp

