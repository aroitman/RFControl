import PyQt5.Qt as Qt
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from CaChannel import ca
from epicsQt import epicsQt, epicsQtPv
import css
import math
import traceback


class e2Label(Qt.QLabel, epicsQt):
    valueChanged = Qt.pyqtSignal()
    def __init__(self, *args, **kwargs):

        pvName = kwargs.pop("pv",None)
        parent = kwargs.pop("parent",None)
        self.digits = int(kwargs.pop("decimals", 3))
        self.text_style = kwargs.pop("text_style", "F")

        super(e2Label, self).__init__(*args, **kwargs)
        epicsQt.__init__(self, pvName=pvName)
        self.setEnabled(False)
        self.setStyleSheet(css.style_property)
        self.setProperty('status', 'disabled')
        self.setStyle(self.style())

    def valueChange(self):
        #print("val changed..")
        try:
            self.set_severity(self.pv.pv_severity)
        except Exception as e:
            print("-----------------------------------")
            print(traceback.format_exc())
            print("-----------------------------------")

        # In case of integer
        if self.pv.field_type() == ca.DBF_INT or \
           self.pv.field_type() == ca.DBF_SHORT or \
           self.pv.field_type() == ca.DBF_LONG:
            if self.text_style == "b": # Print in binary format
                super(e2Label,self).setText(bin(self.pv.pv_value)[2:])
            else:
                super(e2Label,self).setText( "%d" % self.pv.pv_value)

        elif self.pv.field_type() == ca.DBF_DOUBLE or self.pv.field_type() == ca.DBF_FLOAT:
            if hasattr(self.pv, 'pv_precision'):
                pass
                #self.digits = self.pv.pv_precision
            if self.text_style == "F":
                base_format = "%%.%df" % self.digits # --> e.g. with 3: "%.3f"
                text = base_format % self.pv.pv_value
            else: # E.g. if format is E   #if self.format == "E":
                if self.pv.pv_value > 1e-15 or self.pv.pv_value == 0:
                    if self.pv.pv_value == 0:
                        exponent = 0
                    else:
                        exponent  = int(math.floor(math.log10(math.fabs(self.pv.pv_value))))
                    base   = self.pv.pv_value * math.pow(10, -1.0*exponent)
                    base_format = "%%.%df" % self.digits # --> e.g. with 3: "%.3f"
                    base_as_str = base_format % base
                    text = base_as_str + "E%+01d" % exponent
                else:
                    text = "UR/ERR"

        elif self.pv.field_type() == ca.DBF_ENUM:
            try:
                text = self.pv.pv_statestrings[self.pv.pv_value]
            except:
                text = str(self.pv.pv_value)
        else:
            text = str(self.pv.pv_value)
        try:
            if hasattr(self.pv, 'pv_units'):
                text = ' ' + text + ' ' + self.pv.pv_units + ' '
            super(e2Label, self).setText(text)
        except UnboundLocalError:
            text = "UR/ERR"            
            super(e2Label, self).setText(text)
    # This is for initialization through designer
    # Give PV_NAME;digits;style
    def setText(self,text):
        #print("Setting text")
        vals = text.split(';')
        #print("-------------------------")
        #print(vals)
        #print("-------------------------")
        if len(vals) >= 1 and len(vals[0]) >= 1:
            self.setPV(vals[0])
        if len(vals) >= 2:
            self.digits = int(vals[1])
        if len(vals) >= 3:
            self.text_style = vals[2]

    @QtCore.pyqtProperty("QString")
    def linkedPV(self):
        self.pv.name()

    @linkedPV.setter
    def linkedPV(self, text):
        vals = text.split(';')
        
        if len(vals) >= 1:
            try:
                super(e2Label, self.__class__).linkedPV.fset(self,vals[0])
            except:
                print(dir(self))
                raise
        if len(vals) >= 2:
            self.digits = int(vals[1])
        if len(vals) >= 3:
            self.text_style = vals[2]
