import PyQt5.Qt as Qt
from PyQt5 import QtCore, QtGui, QtWidgets
import css
from CaChannel import ca
import epicsPV
import numpy as np

class epicsQt(object):
    """Container class around an EPICS PV for use in a Qt application.
    Merge into a QWidget class (second inheritance)."""
    severityChanged = Qt.pyqtSignal(int)

    def __init__(self, *args, **kwargs):

        pvName = kwargs.pop('pvName', None)
        self.range_warn = [[1e99, 1e99], [-1e99, -1e99]]
        self.range_alarm = [[1e99, 1e99], [-1e99, -1e99]]
        self.severity = -1
        self._percentage = 0.1
        self._mode = 'relative'
        if pvName is not None:
            self.setPV(pvName)
        self.range_warn = None
        self.range_alarm = None

    def set_ranges(self, warn_high, alarm_high, warn_low, alarm_low):
        self.range_warn = [[warn_high, alarm_high], [alarm_low, warn_low]]
        self.range_alarm = [[alarm_high, 1e99], [-1e99, alarm_low]]

    def setCalibration(self, calibration):
        self.pv.calibration = calibration
        if self.pv.inited:
            self.pv.pv_value = self.pv.pv_value * calibration
            self.pv.valueChanged.emit()

    def update_ranges(self):
        if hasattr(self.pv.callBack, 'pv_lowarnlim'):
            lowarn = self.pv.pv_lowarnlim
            if np.isnan(lowarn):
                lowarn = 0
            upwarn = self.pv.pv_upwarnlim
            if np.isnan(upwarn):
                upwarn = 0
            if not lowarn == upwarn == 0:
                lowarn = max(lowarn, self.range_warn[1][1])
                upwarn = min(upwarn, self.range_warn[0][0])
                self.range_warn[1][1] = lowarn
                self.range_warn[0][0] = upwarn
            self.set_severity(self.pv.pv_severity)

        if hasattr(self.pv.callBack, 'pv_loalarmlim'):
            loalarm = self.pv.pv_loalarmlim
            if np.isnan(loalarm):
                loalarm = 0
            upalarm = self.pv.pv_upalarmlim
            if np.isnan(upalarm):
                upalarm = 0
            if not loalarm == upalarm == 0:
                loalarm = max(loalarm, self.range_alarm[1][1])
                upalarm = min(upalarm, self.range_alarm[0][0])
                self.range_warn[0][1] = upalarm
                self.range_warn[1][0] = loalarm
                self.range_alarm[0][0] = upalarm
                self.range_alarm[1][1] = loalarm
            self.set_severity(self.pv.pv_severity)

    def set_ranges(self, warn_high, alarm_high, warn_low, alarm_low):
        self.range_warn = [[warn_high, alarm_high], [alarm_low, warn_low]]
        self.range_alarm = [[alarm_high, 1e99], [-1e99, alarm_low]]
        self.update_ranges()

    @QtCore.pyqtProperty("QString")
    def limits(self, text):
        return str(self.range_warn[1][1]), str(self.range_warn[0][0]), str(self.range_alarm[1][1]), str(self.range_alram[0][0])

    @limits.setter
    def limits(self, text):
        warn_high, alarm_high, warn_low, alarm_low = [float(t) for t in text.split(';')]
        self.set_ranges(warn_high, alarm_high, warn_low, alarm_low)

    @QtCore.pyqtProperty("QString")
    def monitorPV(self):
        return self.pv.name()

    @monitorPV.setter
    def monitorPV(self, pv):
        """Sets up the specified PV."""
        self.monitor = epicsQt(pvName=pv)
        self.monitor.pv.valueChanged.connect(self.setRangeFromMonitor)

    @QtCore.pyqtProperty("QString")
    def monitorValue(self):
        return str(self._value)

    @monitorValue.setter
    def monitorValue(self, value):
        """Sets up the specified PV."""
        self._value = float(value)

    @QtCore.pyqtProperty("QString")
    def monitorMode(self):
        return str(self._mode)

    @monitorMode.setter
    def monitorMode(self, text):
        """Sets up the specified PV."""
        if text.lower() in ['absolute', 'relative']:
            self._mode = text.lower()

    def setRangeFromMonitor(self):
        v = self.monitor.pv.pv_value
        if self._mode.lower() == 'relative':
            mV = self._value / 100
            ranges = (v * (1+mV), v * (1+2*mV),  v * (1-mV), v * (1-2*mV))
        else:
            mV = self._value
            ranges = (v + mV, v + 2 * mV, v - mV, v - 2 * mV)
        self.set_ranges(*ranges)
        self.set_severity(self.pv.pv_severity)

    @QtCore.pyqtProperty("QString")
    def linkedPV(self):
        return self.pv.name()

    @linkedPV.setter
    def linkedPV(self, pv):
        """Sets up the specified PV."""
        self.pv = epicsQtPv(pv)
        if self.pv.inited:
            try:
                self.setEnabled(True)
            except:
                pass
            self.controlInfo()
            self.update_ranges()
            self.valueChange()
        # This should be able to be done before, but gives errors so...
        self.pv.connectionChanged[bool].connect(self.connectionChanged)
        self.pv.controlInfo.connect(self.controlInfo)
        self.pv.controlInfo.connect(self.update_ranges)
        self.pv.valueChanged.connect(self.valueChange)

    def setPV(self, pv):
        self.linkedPV = pv

    def set_severity(self, severity):
        value = self.pv.pv_value
        if not all([self.range_warn is None, self.range_alarm is None]):
            if severity == 3:
                pass
            else:
                severity = 0
                if (value >= self.range_warn[0][0] and value <= self.range_warn[0][1]) or (value >= self.range_warn[1][0] and value <= self.range_warn[1][1]):
                    severity = 1
                if (value >= self.range_alarm[0][0] and value <= self.range_alarm[0][1]) or (value >= self.range_alarm[1][0] and value <= self.range_alarm[1][1]):
                    severity = 2
        else:
            pass
        try:
            if severity == 0:   self.setProperty('status', 'normal')
            elif severity == 1: self.setProperty('status', 'warn')
            elif severity == 2: self.setProperty('status', 'alarm')
            elif severity == 3: self.setProperty('status', 'invalid')
            self.setStyle(self.style())
            if severity != self.severity:
                self.severityChanged.emit(int(severity))
                self.severity = severity
        except:
            if severity != self.severity:
                self.severity = severity
        return severity

    def connectionChanged(self, connected):
        try:
            if connected:
                self.setEnabled(True)
                self.setObjectName(self.pv.name())
            else:
                self.setEnabled(False)
                self.setProperty('status', 'disabled')
                self.setStyle(self.style())
        except:
            pass

    def controlInfo(self):
        pass

    def valueChange(self):
        pass

class epicsQtPv(QtCore.QObject, epicsPV.epicsPV):
    """Container class, extending an EPICS PV with Qt signals."""

    controlInfo = Qt.pyqtSignal()
    valueChanged = Qt.pyqtSignal()
    connectionChanged = Qt.pyqtSignal(bool)

    def __init__(self, pvName=None):
        super(epicsQtPv, self).__init__()
        self.never_conn = True
        self.inited = False
        self.search_and_connect(pvName, self.connectCB)
        self.calibration = 1

    # Callback functions
    def controlCB(self, epicsArgs, _):
        for key in epicsArgs.keys():
            setattr(self, key, epicsArgs[key])
        self.inited = True
        self.controlInfo.emit()

    def valueCB(self, epicsArgs, _):
        for key in epicsArgs.keys():
            setattr(self, key, epicsArgs[key])
        self.pv_value = self.pv_value * self.calibration
        self.valueChanged.emit()

    def connectCB(self, epicsArgs, _):
        conn = epicsArgs[1] == ca.CA_OP_CONN_UP
        # Setup valueCB only in the first time
        if conn and self.never_conn:
            # Register monitor for value and alarm change
            self.add_masked_array_event(ca.dbf_type_to_DBR_STS(self.field_type()), None,
                                        ca.DBE_VALUE | ca.DBE_ALARM, self.valueCB)
            # Retrieve the control information
            self.array_get_callback(ca.dbf_type_to_DBR_CTRL(self.field_type()), None, self.controlCB)
            self.never_conn = False
        self.connectionChanged.emit(conn)
