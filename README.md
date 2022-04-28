# What is this?

This is a daemon to enhance the features in the Logitech Trackball Marble and Logitech MX Anywhere 2S in Linux. It contains services that map the mouse inputs info keys like Back, Forward, Scrolling, Alt+Tab, and so on.

# Usage

## Logitech Trackball Marble

![Buttons](images/keys_marble.png)

Normal Mode

- A : Left click
- B : Back
- C : Right click
- D : Middle click
- E : Move cursor

Holding B

- B + A : Previous window (Alt+Shift+Tab)
- B + C : Forward
- B + D : Next window (Alt + Tab)
- B + E : Vertical and horizontal scrolling

Holding D

- D + A : Go to declaration (Ctrl + Left click)
- D + B : Close tab (Ctrl + W)
- D + C : Close window (Alt + F4)
- D + E : Switch tabs (Ctrl + Tab, Ctrl + Shift + Tab)

## Logitech MX Anywhere 2S

![Buttons](images/keys_mx2s.png)

Normal Mode

- A : Left Click
- B : Middle Click
- C : Right Click
- D : Horizontal Scroll
- E : Vertical Scroll
- F : Horizontal Scroll
- G : Back
- H : Forward

Browser Mode

- G + A : Go to Declaration (Ctrl + Click)
- G + B : Close Tab
- G + C : Restore Tab
- G + D : Zoom In
- G + E : Switch Tabs
- G + F : Zoom Out

Multimedia Mode

- H + A : Play / Pause
- H + B : Stop
- H + C : Mute / Unmute
- H + D : Next Track
- H + E : Volume Up / Down
- H + F : Previous Track

System mode

- H + G : Show windows (Meta key)
- H + G + A : Ctrl + Z
- H + G + B : Close Window
- H + G + C : Ctrl + Shift + Z
- H + G + E : Switch Window

# Dependencies

This daemon requires python3, pip and evdev. It has only been tested in Ubuntu 20.04 LTS, you can install its dependencies with the following commands.

```shell
sudo apt update
sudo apt install -yq libpython3-dev
sudo pip3 install evdev
```

# Install

```shell
# Install the services and python sources for all devices
sudo ./install.sh

# Start the service you want
sudo service marble-svc start # For Logitech Trackball Marble
sudo service mx2s-svc start   # For Logitech MX Anywhere 2S

# Activate autostart during system boot
sudo systemctl enable marble-svc # For Logitech Trackball Marble
sudo systemctl enable mx2s-svc   # For Logitech MX Anywhere 2S
```

# Uninstall

```shell
# Stop services, uninstall them, and remove all files
sudo ./uninstall.sh
```
