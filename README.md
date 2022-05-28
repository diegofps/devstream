# What is this?

These is a system service to enhance the compatibility of the Logitech Trackball Marble, Logitech MX Anywhere 2S, and other devices I may have with the Linux OS. It contains scripts that start during system boot and map the device inputs into special commands, like Back, Forward, Scrolling, Alt+Tab, macros, and so on. If a device is not present/detected it simply ignores the enhancements.

# Usage

## Logitech Trackball Marble

![Buttons](images/keys_marble.png)

### Normal Mode

| Shortcut | Action                                           |
| -------- | ------------------------------------------------ |
| A        | Left Click                                       |
| B        | Go to Declaration / Open New (Ctrl + Left Click) |
| C        | Right Click                                      |
| D        | Middle Click                                     |
| E        | Move Cursor                                      |

### Holding B

| Shortcut | Action                            |
| -------- | --------------------------------- |
| B + A    | Show All Windows (Super)          |
| B + C    | Back                              |
| B + D    | Forward                           |
| B + E    | Vertical and Horizontal Scrolling |

### Holding C

| Shortcut | Action                                               |
| -------- | ---------------------------------------------------- |
| C + A    | Search Selection {+Alt RightClick -Alt S}            |
| C + B    | Reopen Tab (Ctrl + Shift + T)                        |
| C + D    | New Tab (Ctrl + T)                                   |
| C + E    | Change Volume (Vertical) or Undo / Redo (Horizontal) |

### Holding D

| Shortcut | Action                                                |
| -------- | ----------------------------------------------------- |
| D + A    | Close Tab (Ctrl + W)                                  |
| D + B    | Close Window (Alt + F4)                               |
| D + C    | Close Terminal (Ctrl + D)                             |
| D + E    | Switch Tabs (Vertical) or Switch Windows (Horizontal) |

## Logitech MX Anywhere 2S

![Buttons](images/keys_mx2s.png)

### Normal Mode

| Shortcut | Action            |
| -------- | ----------------- |
| A        | Left Click        |
| B        | Middle Click      |
| C        | Right Click       |
| D        | Horizontal Scroll |
| E        | Vertical Scroll   |
| F        | Horizontal Scroll |
| H        | Back              |
| G        | Forward           |
| G + H    | Show All Windows  |

### Browser Mode

| Shortcut | Action                           |
| -------- | -------------------------------- |
| H + A    | Go to Declaration (Ctrl + Click) |
| H + B    | Close Tab                        |
| H + C    | Reopen Tab (Ctrl + Shift + T)    |
| H + D    | Zoom In                          |
| H + E    | Switch Tabs                      |
| H + F    | Zoom Out                         |

### System mode

| Shortcut | Action           |
| -------- | ---------------- |
| G + A    | Ctrl + Z         |
| G + B    | Close Window     |
| G + C    | Ctrl + Shift + Z |
| G + E    | Switch Window    |

### Multimedia Mode

| Shortcut  | Action           |
| --------- | ---------------- |
| G + H + A | Play / Pause     |
| G + H + B | Stop             |
| G + H + C | Mute / Unmute    |
| G + H + D | Next Track       |
| G + H + E | Volume Up / Down |
| G + H + F | Previous Track   |

## Macro Keyboard

![Buttons](images/keys_macros.png)

| Shortcut               | Action                                                                                          |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| REC + MACRO_N          | Start recording / reset recording keyboard input sequence in buffer N (activates blue led)      |
| MACRO_N (blue led on)  | Finish recording the macro (deactivates led)                                                    |
| MACRO_N (blue led off) | Play the recorded sequence of keys                                                              |
| TOGGLE_N               | Toggle macro MACRO_N between two sets, MACRO_1 to MACRO_6 (left) or MACRO_7 to MACRO_12 (right) |
| Yellow led             | Indicates a key is being pressed                                                                |

# Dependencies

This daemon requires python3, pip and evdev. It has only been tested in Ubuntu 20.04 LTS, you can install its dependencies with the following commands.

```shell
sudo apt update
sudo apt install -yq libpython3-dev
sudo pip3 install evdev
```

# Install

```shell
# Install the service and python sources
sudo ./install.sh

# Start the service in the system
sudo service devstream start

# Activate autostart during system boot
sudo systemctl enable devstream
```

# Uninstall

```shell
# Stop services, uninstall them, and remove all files
sudo ./uninstall.sh
```
