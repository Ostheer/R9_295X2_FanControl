# R9_295X2_FanControl
nou waarom heeft die niet zelf een instelbare faan

## Arduino sketch
Listens on serial port for fan speed setting

## Hardware
per channel: IRF540n MOSFET in common-source that drives a fan placed in parallel with a big 2200uF elco.

TODO: Use optical isolator to readout the hall effect rpm sensor

## Python daemon
1.    Read config file
2.    Scan PC for serial ports and try to connect to them
3.    Loop: Check if speed needs to be changed (mandated by either file or temp) and do so

# How to use
1. Check `fan_daemon` if you need to change the config file location and the like
2. Create the directory listed in `fan_daemon` (Something like `~./radeonFanControl`)
3. Place `config` in that directory
4. Place `fan_daemon` in `/usr/bin`
5. `chmod 755` that shit
6. Place `fan_daemon.service` in `/etc/systemd/system`
7. Run `sudo systemctl start fan_daemon.service` (or reboot)
