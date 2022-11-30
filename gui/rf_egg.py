import spinmob.egg as egg
import sys
from PyQt5 import QtWidgets, QtCore
from epics import PV
from e2Label import e2Label

prefix = "Beamline:RF"
pvs = {"Vset": PV(prefix + ":setVoltage"), "Iset": PV(prefix + ":setCurrent"), "PSset": PV(prefix + ":setPSState"), "SWset": PV(prefix + ":setSWState"), "Hzset": PV(prefix + ":setFrequency"), "Vget": PV(prefix + ":getVoltage"), "Iget": PV(prefix + ":getCurrent"), "PSget": PV(prefix + ":getPSUState"), "SWget": PV(prefix + ":getSWState"), "Hzget": PV(prefix + ":getFrequency"), "running": PV(prefix + ":isRunning"), "matching": PV(prefix + ":isMatching")}


window = egg.gui.Window("RF EGG")
t1 = window.place_object(egg.gui.TabArea())
t2 = window.place_object(egg.gui.TabArea())

t1_c = t1.add_tab("Control Values")
t2_r = t2.add_tab("Read Values")


t2_r.place_object(egg.gui.Label("Voltage (V):"))
getV = t2_r.place_object(e2Label(), alignment=0, column_span=3)
getV.setText(pvs["Vget"].pvname)
t2_r.new_autorow()
t2_r.place_object(egg.gui.Label("Current (A):"))
getI = t2_r.place_object(e2Label(), alignment=0, column_span=3)
getI.setText(pvs["Iget"].pvname)
t2_r.new_autorow()
t2_r.place_object(egg.gui.Label("Frequency (MHz):"))
getHz = t2_r.place_object(e2Label(), alignment=0, column_span=3)
getHz.setText(pvs["Hzget"].pvname)
t2_r.new_autorow()
t2_r.place_object(egg.gui.Label("RF PS Status:"))
getPS = t2_r.place_object(e2Label(), alignment=0, column_span=3)
getPS.setText(pvs["PSget"].pvname)
t2_r.new_autorow()
t2_r.place_object(egg.gui.Label("RF Switch Status:"))
getSW = t2_r.place_object(e2Label(), alignment=0, column_span=3)
getSW.setText(pvs["SWget"].pvname)
t2_r.new_autorow()

t1_c.place_object(egg.gui.Label("Voltage (V):"))
setVsb = t1_c.place_object(QtWidgets.QDoubleSpinBox(maximum=100000))
t1_c.new_autorow()
t1_c.place_object(egg.gui.Label("Current (A):"))
setIsb = t1_c.place_object(QtWidgets.QDoubleSpinBox(maximum=100000))
t1_c.new_autorow()
t1_c.place_object(egg.gui.Label("Frequency (Hz):"))
setHzsb = t1_c.place_object(QtWidgets.QDoubleSpinBox(maximum=100000))
t1_c.new_autorow()
t1_c.place_object(egg.gui.Label("RF PS Status:"))
setPSsb = t1_c.place_object(QtWidgets.QSpinBox(maximum=1, wrapping=True))
t1_c.new_autorow()
t1_c.place_object(egg.gui.Label("RF SW Status:"))
setSWsb = t1_c.place_object(QtWidgets.QSpinBox(maximum=7, wrapping=True))
setSWsb.setSingleStep(7)
t1_c.new_autorow()
apply_button = t1_c.place_object(egg.gui.Button("Apply patterns"))


window.new_autorow()
run_status = egg.gui.Label("EPICS running:")
match_status = egg.gui.Label("get and set variables matching:")
window.place_object(run_status)
window.place_object(match_status)


def updateSBs(**kw):
    pv_vals = {}
    for name in ["Vset", "Iset", "PSset", "SWset", "Hzset"]:
        pv_vals[name] = pvs[name].get()
    if None not in pv_vals.values():
        setVsb.setValue(pvs["Vset"].get())
        setIsb.setValue(pvs["Iset"].get())
        setHzsb.setValue(pvs["Hzset"].get())
        setPSsb.setValue(pvs["PSset"].get())
        setSWsb.setValue(pvs["SWset"].get())


updateSBs()
for keys in pvs:
    pvs[keys].add_callback(updateSBs)


def updatePVs():
    pvs["Iset"].put(setIsb.value())
    pvs["Vset"].put(setVsb.value())
    pvs["PSset"].put(setPSsb.value())
    pvs["SWset"].put(setSWsb.value())
    pvs["Hzset"].put(setHzsb.value())


window.connect(apply_button.signal_clicked, updatePVs)


# connect a timer to update the matching and running PVs every 5 seconds
def updateRunMatch():
    if (pvs["running"].get() is not None) and (pvs["running"].get() != 0):
        run_status.set_text("EPICS running: YES")
    else:
        run_status.set_text("EPICS running: NO")
    if (pvs["matching"].get() is not None) and (pvs["matching"].get() != 0):
        match_status.set_text("get and set variables matching: YES")
    else:
        match_status.set_text("get and set variables matching: NO")


updateRunMatch()
timer = QtCore.QTimer()
timer.timeout.connect(updateRunMatch)
timer.start(5000)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window.show()
    sys.exit(app.exec_())
