#!/usr/bin/env bash

echo "Stopping service..."
service logitech-marble stop

echo "Removing service..."
update-rc.d logitech-marble remove

echo "Removing files..."
rm /etc/init.d/logitech-marble
rm -rf /etc/marble_daemon

echo "Uninstall completed"
