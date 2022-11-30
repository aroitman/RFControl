from PyQt5.QtCore import *


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os, datetime

import pyqtgraph as pg

import re
import numpy as np

# import fancySpin

# Give it a combobox (2 RFQ extraction) and a list of available choices for comboboxes
# Returns channel(s)
def getPulseBlasterChannelNumbers(combobox, action_choices):
    # Get index of the combobox
    index = combobox.currentIndex()
    
    # Then get the channels from the correspoind action_choices
    channels = []
    for i in action_choices[index][1]:
        channels.append(i)
    return channels
    
def getBinBordersForUnevenlySpacedData(datapoints):
    datapoints_int = [(int(x*1000.)) for x in datapoints]
    unique_scan_points = list(set(datapoints_int))
    unique_scan_points.sort()
    unique_scan_points = [(x/1000.) for x in unique_scan_points]
    
    bin_borders = []
    if len(unique_scan_points) >= 2:
        #print("check len(scan points)=",len(unique_scan_points))
        bin_borders.append( (3*unique_scan_points[0]-unique_scan_points[1])/2. ) # border left of array
        for i in range(0,len(unique_scan_points)-1):
            bin_borders.append( (unique_scan_points[i]+unique_scan_points[i+1])/2. ) # middle borders
        bin_borders.append((3*unique_scan_points[-1]-unique_scan_points[-2])/2.) # last border
    elif len(unique_scan_points) == 1: # in case only one scan point
        #print("daa")
        bin_borders.append(unique_scan_points[0]-1.)
        bin_borders.append(unique_scan_points[0]+1.)
    else:
        return [0,1], 0
    return bin_borders, len(unique_scan_points)
    

def get_name_val_for_gui_widget(widget):
    name = None
    value = None
    if isinstance(widget, QComboBox):
        name = widget.objectName()  # get combobox name
        value = widget.currentIndex()  # get current index from combobox

    elif isinstance(widget, QLineEdit):
        name = widget.objectName()
        value = widget.text()

    elif isinstance(widget, QCheckBox):
        name = widget.objectName()
        value = widget.isChecked()

    elif isinstance(widget, QRadioButton):
        name = widget.objectName()
        value = widget.isChecked()  # get stored value from registry

    elif isinstance(widget, QSpinBox):
        name  = widget.objectName()
        value = widget.value()             # get stored value from registry

    elif isinstance(widget, QDoubleSpinBox):
        name  = widget.objectName()
        value = widget.value()             # get stored value from registry

    return name, value
    
def if_name_matches_set_val_for_gui_widget(widget, key, val):
    val_bool = False

    # Somehow if loaded from file the value is string
    # But if saving and loading within same session,
    # the value appears to be boolean...
    if val == "true" or val == True: 
        val_bool = True
        
#    if val == "true" or val == "false":
 #       print("key val",key,val)
  #      print("widget", widget.objectName())
    if isinstance(widget, QComboBox):
        if widget.objectName() == key:  
            widget.setCurrentIndex(int(val))

    elif isinstance(widget, QLineEdit):
        if widget.objectName() == key:  
            widget.setText(val)
            widget.editingFinished.emit()

    elif isinstance(widget, QCheckBox):
        if widget.objectName() == key:  
            widget.setChecked(val_bool)
            widget.stateChanged.emit(widget.checkState())
            #print("key val val_bool widget",key,val,val_bool,widget.objectName())

    elif isinstance(widget, QRadioButton):
        if widget.objectName() == key:  
            widget.setChecked(val_bool)  # get stored value from registry

    elif isinstance(widget, QSpinBox):
        if widget.objectName() == key:  
            widget.setValue(int(val))             # get stored value from registry

    elif isinstance(widget, QDoubleSpinBox):
        if widget.objectName() == key:  
            widget.setValue(float(val))
    else:
        pass
        #print("da fug ", key, val)

def is_widget_saveworthy(widget):
    if isinstance(widget, QComboBox):
        return True

    elif isinstance(widget, QLineEdit):
        return True

    elif isinstance(widget, QCheckBox):
        return True

    elif isinstance(widget, QRadioButton):
        return True

    elif isinstance(widget, QSpinBox):
        return True

    elif isinstance(widget, QDoubleSpinBox):
        return True
    else:
        pass
    return False


def gauss(x, A, mu, sigma):
    
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))
    
def ensure_dir(dirr):
    if not os.path.exists(dirr):
        os.makedirs(dirr)
        
def create_backup_save_dir(description="",basepath="T:\\JYFLTRAP_autosave"):
    root = basepath
    today = datetime.datetime.now()
    rootpath = os.path.abspath(root)
    savepath = os.path.join(rootpath,today.strftime("%Y"),today.strftime("%m"),today.strftime("%d"),today.strftime("%H_%M_")+description)
    for i in range(1,20,1):
        try_path = savepath + "_%d" % i
        if not os.path.isdir(try_path): # Not existing? Then create it and return
            ensure_dir(try_path)
            return try_path
        

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        #return [datetime.datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
        return [datetime.datetime.fromtimestamp(value).strftime('%d/%m %H:%M')
            for value in values]

def get_scan_point_number(scan_from,scan_to,scan_step):
    return int((int(abs((scan_from - scan_to)*1000))+int(abs(scan_step*1000))) / int(abs(scan_step*1000)))


def get_scan_points(scan_pars):
    epics_points = []
    #print("from %.3f to %.3f" %(scan_pars["scan from"],scan_pars["scan to"]))

    # scan from low to high value
    if scan_pars["scan from"] <= scan_pars["scan to"]:
        epics_point = int(scan_pars["scan from"]*1000)
        while epics_point <= int(scan_pars["scan to"]*1000):
            epics_points.append( epics_point/1000.)
            epics_point = epics_point + int(scan_pars["scan step"]*1000)
    else:
        print ("high -> low val scan")
        epics_point = int(scan_pars["scan from"]*1000)
        while epics_point >= int(scan_pars["scan to"]*1000):
            epics_points.append( epics_point/1000.)
            epics_point = epics_point - int(scan_pars["scan step"]*1000)

    #print("epics points %d" % len(epics_points))

    return epics_points


def get_number_as_text_from_string(string):
    non_decimal = re.compile(r'[^\d.-]+') # Removes all but numbers, . and -

    return non_decimal.sub('', string)

#def get_timestamp_as_nice_datetime_format(timestamp):
#    value1 = datetime.datetime.fromtimestamp().strftime('%Y-%m-%d %H:%M:%S')
#    
#    mean_datetime.strftime('%Y-%m-%d %H:%M:%S')

def is_box_at_its_minimum(box):
    if isinstance(box, QSpinBox) or isinstance(box, QDoubleSpinBox):
        if box.value() == box.minimum():
            return True
        else:
            return False
    else: #Case of fancyspin
        if box.value == box.minimum:
            return True
        else:
            return False

def is_box_at_its_maximum(box):
    if isinstance(box, QSpinBox) or isinstance(box, QDoubleSpinBox):
        if box.value() == box.maximum():
            return True
        else:
            return False
    else: #Case of fancyspin
        if box.value == box.maximum:
            return True
        else:
            return False

def arctan2_0_360(y,x):
    angle = np.arctan2(y,x)*180/np.pi
    if angle < 0:
        angle = angle + 360
    return angle

def save_widget_settings(qt_core_q_settings, widgets):
    for i in widgets:
        name, val = get_name_val_for_gui_widget(i)
        if name is not None and val is not None:
            qt_core_q_settings.setValue(name, val)

def load_widget_settings(qt_core_q_settings,widgets):
    #print("key val ", key, settings.value(key), settings.value(key))
    for key in qt_core_q_settings.allKeys():
        for i in widgets:
            if_name_matches_set_val_for_gui_widget(
                    i, key, qt_core_q_settings.value(key))  
