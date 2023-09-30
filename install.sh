#!/usr/bin/env bash


set -e


echo "Building canvas2..."
mkdir -p ./build/canvas2
cd ./build/canvas2
qmake6 CONFIG+=release -o Makefile ../../canvas2/canvas2.pro
make -j`nproc`
cd ../..


echo "Copying files..."
mkdir -p /etc/devstream
cp -r ./*.py shadows /etc/devstream/
cp ./devstream /etc/init.d/devstream
cp ./build/canvas2/canvas2 /etc/devstream/canvas2.release


echo "Configuring service..."
chmod +x /etc/init.d/devstream
update-rc.d devstream defaults


echo "Installation completed"
