#!/usr/bin/env bash

echo "Stopping service..."
service marble-svc stop
service mx2s-svc stop


echo "Removing service..."
update-rc.d marble-svc remove
update-rc.d mx2s-svc remove


echo "Removing files..."
rm /etc/init.d/marble-svc
rm /etc/init.d/mx2s-svc

rm -rf /etc/logitech_wrappers

echo "Uninstall completed"
