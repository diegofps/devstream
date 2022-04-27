# What is this?

This is a daemon to enhance the features in the Logitech Trackball Marble and Logitech MX Anywhere 2S in Linux. It contains services that map the mouse inputs info keys like Back, Forward, Scrolling, Alt+Tab, and so on.

# Usage

## Logitech Trackball Marble

![Buttons](images/keys_marble.png)

- A : Left click
- B : Alternate mode
- C : Right click
- D : Middle click
- E : Move cursor

- B + A : Alt + Tab
- B + C : Back
- B + D : Forward
- B + E : Vertical and horizontal scrolling

## Logitech MX Anywhere 2S

![Buttons](images/keys_mx2s.png)

Normal Mode

- A : Left Click
- B : Middle Click
- C : Right Click
- D : Go Forward
- E : Vertical Scroll
- F : Go Back

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

- H+G + A : Ctrl+Z
- H+G + B : Close Window
- H+G + C : Ctrl+Y
- H+G + E : Switch Window

# Dependencies

This daemon requires python3, pip and evdev. It has only been tested in Ubuntu 20.04 LTS and you can install its dependencies with the following commands.

```shell
sudo apt update
sudo apt install -yq libpython3-dev
pip3 install evdev
```

# Install

```shell
// Install the services and python sources
sudo ./install.sh

// Start the service you want
sudo service marble-svc start // For Logitech Trackball Marble
sudo service mx2s-svc start   // For Logitech MX Anywhere 2S

// Activate autostart during system boot
sudo systemctl enable marble-svc // For Logitech Trackball Marble
sudo systemctl enable mx2s-svc   // For Logitech MX Anywhere 2S
```

# Uninstall

```shell
sudo ./uninstall.sh
```
