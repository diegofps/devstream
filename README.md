# What is this?

These are system services to enhance the compatibility of the Logitech Trackball Marble and Logitech MX Anywhere 2S with Linux. It contains scripts that start during system boot and map the device inputs into commands, like Back, Forward, Scrolling, Alt+Tab, and so on.

# Usage

## Logitech Trackball Marble

![Buttons](images/keys_marble.png)

Normal Mode

- A : Left Click
- B : Back
- C : Right Click
- D : Middle Click
- E : Move Cursor

Holding B

- B + A : Reopen Tab (Ctrl + Shift + T)
- B + C : Forward
- B + D : Show All Windows
- B + E : Vertical and Horizontal Scrolling

Holding D

- D + A : Go to Declaration (Ctrl + Left Click)
- D + B : Close Tab (Ctrl + W)
- D + C : Close Window (Alt + F4)
- D + E : Switch Tabs (Vertical) or Switch Windows (Horizontal)

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

Multimedia Mode

- H + A : Play / Pause
- H + B : Stop
- H + C : Mute / Unmute
- H + D : Next Track
- H + E : Volume Up / Down
- H + F : Previous Track

Browser Mode

- G + A : Go to Declaration (Ctrl + Click)
- G + B : Close Tab
- G + C : Reopen Tab (Ctrl + Shift + T)
- G + D : Zoom In
- G + E : Switch Tabs
- G + F : Zoom Out

System mode

- G + H : Show All Windows
- G + H + A : Ctrl + Z
- G + H + B : Close Window
- G + H + C : Ctrl + Shift + Z
- G + H + E : Switch Window

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
