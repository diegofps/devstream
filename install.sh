#!/usr/bin/env bash

echo "Copying files..."
mkdir -p /etc/marble_daemon
cp ./main.py /etc/marble_daemon/
cp ./logitech-marble /etc/init.d/logitech-marble

echo "Configuring service..."
chmod +x /etc/init.d/logitech-marble
update-rc.d logitech-marble defaults
systemctl enable logitech-marble

echo "Starting service..."
service logitech-marble start

echo "Installation completed"
