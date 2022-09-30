# RFControl

A Python interface for our RF Power Supply and our RF Switch.


## Description of Files
- `rfps.py, rfswitch.py` Python DLL wrappers for power supply and switch, respectively.
- `rfbackend.py` Python EPICS backend for the PS and switch, fully tested now.
- `RF.template` EPICS PV template folder which you can use to create the EPICS PVs needed for the backend

## How to use
To start the EPICS backend, from the project directory, run
```
python3 rfbackend.py
```
Make sure you have the EPICS variables defined beforehand. Put the provided template file in the respective folder in your EPICS setup. Then, in the substitutions folder, input the following:
```
file "/path/to/RF.template" { pattern
{P, R, PREC}
{Beamline, RF, 1}
}
```
Or you can manually define the PVs if you wish.

## To Be Implemented
- GUI
