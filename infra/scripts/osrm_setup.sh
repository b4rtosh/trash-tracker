#!/bin/bash
set -e

# Log everything
exec > >(tee /var/log/osrm-setup.log)
exec 2>&1

echo "Starting OSRM data preparation..."

# Update system
yum update -y

# Install Docker
yum install -y docker amazon-efs-utils

# Start Docker service
systemctl start docker
systemctl enable docker

# Mount EFS
echo "Mounting EFS ${efs_id}..."
mkdir -p /mnt/efs
mount -t efs -o tls ${efs_id}:/ /mnt/efs

# Check if data already exists
if [ -f /mnt/efs/.osrm-ready ]; then
    echo "OSRM data already prepared. Skipping..."
    shutdown -h now
    exit 0
fi

# Download map data
echo "Downloading map data from ${map_data_url}..."
cd /mnt/efs
wget ${map_data_url} -O dolnoslaskie-latest.osm.pbf

# Process OSRM data
echo "Running osrm-extract..."
docker run -t -v "/mnt/efs:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/dolnoslaskie-latest.osm.pbf

echo "Running osrm-partition..."
docker run -t -v "/mnt/efs:/data" osrm/osrm-backend osrm-partition /data/dolnoslaskie-latest.osrm

echo "Running osrm-customize..."
docker run -t -v "/mnt/efs:/data" osrm/osrm-backend osrm-customize /data/dolnoslaskie-latest.osrm

# Create completion marker
touch /mnt/efs/.osrm-ready
echo "OSRM data preparation completed successfully!"

# Shutdown instance to save costs
echo "Shutting down instance..."
shutdown -h now