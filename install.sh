#!/usr/bin/env bash


echo "Copying files..."
mkdir -p /etc/logitech_wrappers
cp ./*.py /etc/logitech_wrappers/
cp ./marble-svc /etc/init.d/marble-svc
cp ./mx2s-svc /etc/init.d/mx2s-svc


echo "Configuring service..."
chmod +x /etc/init.d/marble-svc
chmod +x /etc/init.d/mx2s-svc

update-rc.d marble-svc defaults
update-rc.d mx2s-svc defaults


echo "Installation completed"
