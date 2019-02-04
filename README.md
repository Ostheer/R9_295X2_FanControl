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
