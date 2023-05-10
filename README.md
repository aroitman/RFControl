# RFControl

A Python Interface for CGC Instruments' Double Power Supply Unit and the radio-frequency AMX Switch.

Power Supply: https://www.cgc-instruments.com/en/Products/Power-Supplies/19PSU/Modules/PSU-CTRL-2D

Switch: https://www.cgc-instruments.com/en/Products/Switches/19AMX/Modules/AMX-CTRL-4ED



## Description of Files
- `rfps.py, rfswitch.py` Python DLL wrappers for power supply and switch, respectively.
- `rfbackend.py` Python EPICS backend for the PS and switch, fully tested now.
- `RF.template` EPICS PV template folder which you can use to create the EPICS PVs needed for the backend

## How to use
### EPICS Backend
To start the EPICS backend, from the project directory, run
```
python3 rfbackend.py
```
Make sure you have the EPICS variables defined beforehand. Put the provided RF template file in your EPICS template directory. Then, in the substitutions file, input the following:
```
file "/path/to/RF.template" { pattern
{P, R, PREC}
{Beamline, RF, 1}
}
```
Or you can manually define the PVs if you wish.

### GUI
once the EPICS backend is started, open up another terminal window, go to the main project directory, and run
```
cd gui
python3 rf_egg.py
```
Now, you can control both the power supply and the switch through a GUI.
