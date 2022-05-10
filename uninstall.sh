#!/usr/bin/env bash


set -e


echo "Stopping service..."
service devstream stop


echo "Removing service..."
update-rc.d devstream remove


echo "Removing files..."
rm /etc/init.d/devstream
rm -rf /etc/devstream

echo "Uninstall completed"
