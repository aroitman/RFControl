
A Python Interface for CGC Instruments' Double Power Supply Unit and the radio-frequency AMX Switch.

Power Supply: https://www.cgc-instruments.com/PSU-CTRL-2D

Switch: https://www.cgc-instruments.com/AMX-CTRL-4ED

## Installation
Currently, only Windows is supported.

Install [Anaconda](https://anaconda.com). Open the anaconda prompt and install the needed dependencies with the following commands:

```
conda install -c paulscherrerinstitute pcaspy
conda install conda-forge::pyepics
conda install paulscherrerinstitute::cachannel
conda install anaconda::pyqt
conda install pip
pip install spinmob
```
You will also need the DLLs for the CGC power supply and switch, make a note of their file locations.

Finally, clone the repository by running
```
git clone https://github.com/aroitman/RFControl
```
## How to use
### Config
Edit the `config.py` file and input the location of the power supply dll and switch dll for the `ps_loc` and `switch_loc` variables, respectively. Next, specify which comm ports to use for the power supply and the switch with the `ps_com` and `switch_com` variables, respectively. Set the prefix to use for your EPICS PVs with the `epics_prefix` variable. 


### Start the Backend
To start the EPICS backend, open an anaconda prompt and cd to the project directory. Then, run
```
python epics_server.py
```
In another anaconda prompt, run
```
python rfbackend.py
```
### Start the GUI
cd to the `gui` folder and run
```
python rf_egg.py
```
This gui can be run on any computer connected to the same subnetwork as the EPICS server. Further documentation about the functions used to control and monitor the RF switch and power supply can be found in the `docs` directory or at https://aroitman.github.io/RFControl/.

## Description of Files and Folders
- `rfps.py, rfswitch.py` Python DLL wrappers for power supply and switch, respectively.
- `rfbackend.py` Python EPICS backend for the PS and switch.
- `epics_server.py` EPICS server written using `pcaspy` which creates the PVs necessary for the backend
- `gui/` Folder with the GUI for controlling the power supply and switch, written using the `spinmob` Python package
- `docs/` Folder with documentation about RFControl.

