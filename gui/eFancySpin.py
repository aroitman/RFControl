import PyQt5.Qt as Qt
from PyQt5 import QtCore
from epicsQt import epicsQt
import css
from CaChannel import ca, CaChannel
from fancySpin import fancySpin

class eFancySpin(fancySpin, epicsQt):
    def __init__(self, *args, **kwargs):

        pvName = kwargs.pop("pv",None)
        parent = kwargs.pop("parent",None)
        digits = kwargs.pop("decimals", 3)

        super(eFancySpin, self).__init__(*args, **kwargs)
        epicsQt.__init__(self, pvName=pvName)
        self.setPrecision(digits)
        if pvName is not None:
            self.setPV(pvName)
        self.setEnabled(False)

    def editingFinishedInBox(self,val):
        #print("val changed in eFSB: ", str(self.pv.pv_value))
        self.pv.putWait(self.value)
        #self.pv.array_put(self.value)

    def controlInfo(self):
        # 2019-05-02 
        self.pv.getControl() # Get precision and other pv-related attributes
        lolim = None; uplim = None
        if hasattr(self.pv.callBack, 'pv_loctrllim'):
            #print("has lowlim ", self.pv.pv_loctrllim)
            lolim = self.pv.pv_loctrllim
            self.setMinimum(lolim)
        if hasattr(self.pv.callBack, 'pv_upctrllim'):
            uplim = self.pv.pv_upctrllim
            self.setMaximum(uplim)

        # to avoid stupid lazy developers who put lowlim=uplim=0.0
        if lolim == uplim:
            self.setRange(-1e20, 1e20)

        if self.pv.field_type() == ca.DBF_INT or self.pv.field_type() == ca.DBF_LONG \
            or self.pv.field_type() == ca.DBF_SHORT or self.pv.field_type() == ca.DBF_ENUM:
           prec = 0
        else:
            if not hasattr(self.pv, 'pv_precision'):
                prec = 3
            else:
                prec = self.pv.pv_precision

                #Dirty failsafe for bad isegs having precision set to zero
                if "ISEG" in self.pv.name() and prec == 0:
                    prec = 3

                #This is failsafe in case the precision is set to zero, make it 3 after all
                #if prec == 0:
                #    prec = 3
        #print("presision", prec)
        #self.setDecimals(prec)

        # Don't enable units; just makes trouble with copy-paste
        #if hasattr(self.pv, 'pv_units'):
        #    self.setSuffix(' ' + self.pv.pv_units)
        
        # Allow local changes only after we have got control info of PV.
        self.valueChanged.connect(self.editingFinishedInBox)

        # Initial setting, since it does not always work?
        self.valueChange()

    def valueChange(self):
        self.set_severity(self.pv.pv_severity)
        # if self.pv.pv_severity == 0: self.setProperty('status', 'normal')
        # elif self.pv.pv_severity == 1: self.setProperty('status', 'warn')
        # elif self.pv.pv_severity == 2: self.setProperty('status', 'alarm')
        # elif self.pv.pv_severity == 3: self.setProperty('status', 'invalid')
        # self.setStyle(self.style())
        self.blockSignals(True)
        self.setValue(self.pv.pv_value)
        # For fancyspin just @value.setter
        self.value = self.pv.pv_value
        self.blockSignals(False)
        
    def linkToLabel(self, label, percentage):
        self.percentage = percentage
        self.connected_label = label
        self.pv.valueChanged.connect(self.set_range_on_label)

    def set_range_on_label(self):
        v = self.pv.pv_value
        ranges = (v * (1+self.percentage), v * (1+2*self.percentage),  v * (1-self.percentage), v * (1-2*self.percentage))
        self.connected_label.set_ranges(*ranges)

    # def connectionChanged(self, connected):
    #     if connected:
    #         self.setEnabled(True)
    #     else:
    #         self.setEnabled(False)
    #         self.setproperty('status', 'disabled')
    #         self.setStyle(self.style())


    # This is for initialization through designer
    # Give PV_NAME;digits
    def setText(self,text):
        #print("Setting text")
        #print(text)
        vals = text.split(';')
        #print(vals)
        if len(vals) == 2:
            self.setDecimals(int(vals[1]))
            self.setPV(vals[0])
        # when e.g. loading setting
        if len(vals) == 1: 
            if self.isEnabled():
                if self.pv.field_type() ==  ca.DBF_INT or \
                   self.pv.field_type() ==  ca.DBF_SHORT or \
                   self.pv.field_type() ==  ca.DBF_LONG:
                    self.pv.array_put(int(text))
                elif self.pv.field_type() ==  ca.DBF_FLOAT or \
                   self.pv.field_type() ==  ca.DBF_DOUBLE:
                    self.pv.array_put(float(text))
        else:
            pass

    @QtCore.pyqtProperty("QString")
    def linkedPV(self):
        self.pv.name()

    @linkedPV.setter
    def linkedPV(self, text):
        vals = text.split(';')
        
        if len(vals) >= 1:
            super(eFancySpin, self.__class__).linkedPV.fset(self,vals[0])
        if len(vals) >= 2:
            self.setDecimals(int(vals[1]))
