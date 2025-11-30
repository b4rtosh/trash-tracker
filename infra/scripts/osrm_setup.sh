#!/bin/bash

# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# go to mounted filesystem
cd /mnt/efs/fs1/

# Download map data
sudo wget https://download.geofabrik.de/europe/poland/dolnoslaskie-latest.osm.pbf -O dolnoslaskie-latest.osm.pbf

# extract
sudo docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/dolnoslaskie-latest.osm.pbf
# partition
sudo docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/dolnoslaskie-latest.osrmsudo docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/dolnoslaskie-latest.osrm
# customize
sudo docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/dolnoslaskie-latest.osrmsudo docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/dolnoslaskie-latest.osrm

shutdown -h now