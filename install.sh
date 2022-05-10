#!/usr/bin/env bash


set -e


echo "Copying files..."
mkdir -p /etc/devstream
cp ./*.py /etc/devstream/
cp ./devstream /etc/init.d/devstream


echo "Configuring service..."
chmod +x /etc/init.d/devstream
update-rc.d devstream defaults


echo "Installation completed"
