from queue import Queue
from epics import PV
import time

# dummy mode for testing
mode = "real"
if mode == "real":
    import rfps
    import rfswitch


class RFBackend:
    def __init__(self, name, PSPortNumber, PSCOMNumber, SWPortNumber, SWCOMNumber):
        # initialize ps wrapper
        self.PSPortNumber = PSPortNumber
        self.PSCOMNumber = PSCOMNumber
        self.SWPortNumber = SWPortNumber
        self.SWCOMNumber = SWCOMNumber
        if mode == "real":
            # initialize PS wrapper
            self.rfps = rfps.RFPS(self.PSPortNumber, self.PSCOMNumber)
            self.rfps.open()
            self.rfps.setup()

            # initialize switch wrapper
            self.rfswitch = rfswitch.RFSwitch(self.SWPortNumber, self.SWCOMNumber)
            self.rfswitch.open()
            self.rfswitch.setup()

        # Initialize EPICS set PVs as dictionary
        self.setPVs = {"V": PV(name + ":setVoltage"), "I": PV(name + ":setCurrent"), "PS": PV(name + ":setPSState"), "SW": PV(name + ":setSWState"), "Hz": PV(name + ":setFrequency")}
        # set function dictionary to make setting variables easier
        if mode == "real":
            self.setfunctions = {"V": self.safe_set_output_voltage, "I": self.rfps.set_output_current, "PS": self.ps_change_state, "SW": self.rfswitch.set_controller_config, "Hz": self.rfswitch.set_oscillator_frequency}
        # received and current PV dict to check the epics value with the rf value
        self.received_setPVs = {"V": None, "I": None, "PS": None, "SW": None, "Hz": None}
        self.current_setPVs = {"V": None, "I": None, "PS": None, "SW": None, "Hz": None}

        # Initialize EPICS get PVs as dictionary (PVs read from RF switch and ps)
        self.getPVs = {"V": PV(name + ":getVoltage"), "I": PV(name + ":getCurrent"), "SW": PV(name + ":getSWState"), "Vlim": PV(name + ":getVoltageLimit"), "Ilim": PV(name + ":getCurrentLimit"), "ilock": PV(name + ":getInterlock"), "FR": PV(name + ":getFullRange"), "PS": PV(name + ":getPSUState"), "Hz": PV(name + ":getFrequency")}

        # make the set PVs equal to the get PVs at initialization:
        self.read()
        for key in self.setPVs:
            self.setPVs[key].put(self.getPVs[key])

        self.epicsRunning = PV(name + ":isRunning")
        self.epicsRunning.put("YES")

        # epics values matches the rf values
        self.epicsMatches = PV(name + ":isMatching")
        self.epicsMatches.put("YES")

        # Initialize Queue
        self.sendQueue = Queue()
        self.maxSendBufferLength = 2

        # bind functions to changes in epics variables
        self.setPVs["V"].add_callback(self.setVChanged)
        self.setPVs["I"].add_callback(self.setIChanged)
        self.setPVs["PS"].add_callback(self.setPSChanged)
        self.setPVs["SW"].add_callback(self.setSWChanged)
        self.setPVs["Hz"].add_callback(self.setHzChanged)

        # put a read command into the Queue
        self.sendQueue.put("read")
        self.run()

    def run(self):
        try:
            while True:
                if self.sendQueue.qsize() <= self.maxSendBufferLength:
                    self.sendQueue.put("read")

                request = self.sendQueue.get()
                if request == "read":
                    if mode == "real":
                        time.sleep(1)
                        self.read()
                    else:
                        time.sleep(1)
                        for key in self.getPVs:
                            self.getPVs[key].put(0)
                            print(key, self.getPVs[key].get())
                else:
                    if mode == "real":
                        self.set_value(request)
                    else:
                        self.epicsMatches.put("YES")
                        print("Currently in dummy mode. Set variables changed. Request received:", request)
        except KeyboardInterrupt:
            self.rfps.shutdown()
            self.rfps.close()
            self.rfswitch.shutdown()
            self.rfswitch.close()

    def read(self):
        self.getPVs["V"].put(self.rfps.get_output_voltage(0))
        self.getPVs["I"].put(self.rfps.get_output_current(0))
        self.getPVs["SW"].put(self.rfswitch.get_controller_state())
        self.getPVs["Vlim"].put(self.rfps.get_PSU_set_output_voltage(0)[1])
        self.getPVs["Ilim"].put(self.rfps.get_PSU_set_output_current(0)[1])
        print("oscillator frequency from switch:", self.rfswitch.get_oscillator_frequency())
        self.getPVs["Hz"].put(self.rfswitch.get_oscillator_frequency())
        print("epics value for frequency", self.getPVs["Hz"].get())
        # sets following variables to True if and only if results of the rfps functions are (True, True), otherwise, return False.
        self.getPVs["PS"].put(min(self.rfps.get_PSU_enable()))
        self.getPVs["ilock"].put(min(self.rfps.get_interlock_enable()))
        self.getPVs["FR"].put(min(self.rfps.get_PSU_full_range()))
        for key in self.getPVs:
            print(key, self.getPVs[key].get())

    def setVChanged(self, **kw):
        self.sendQueue.put("V")

    def setIChanged(self, **kw):
        self.sendQueue.put("I")

    def setPSChanged(self, **kw):
        self.sendQueue.put("PS")

    def setSWChanged(self, **kw):
        self.sendQueue.put("SW")

    def setHzChanged(self, **kw):
        self.sendQueue.put("Hz")

    # helper function to change ps state
    def ps_change_state(self, state):
        if state == 1:
            self.rfps.setup()
            return 1
        else:
            self.rfps.shutdown()
            return 0

    # helper function to set voltage safely
    def safe_set_output_voltage(self, voltage):
        self.rfswitch.set_controller_config(0)
        self.rfps.set_output_voltage(voltage)
        self.rfswitch.set_controller_config(7)
        return self.rfps.get_output_voltage(0)

    # function to safely set variables
    def set_value(self, request):
        if request == "SW":
            # need to have an integer for the switch state, 0 or 7
            self.received_setPVs[request] = int(self.setPVs[request].get())
        else:
            self.received_setPVs[request] = self.setPVs[request].get()

        # check whether we are connected to the epics server
        if (self.epicsRunning.get() is None) or (self.epicsRunning.get() == 0):
            print("Connection to EPICS server lost")
        # set values on RF to the values received from EPICS
        result = self.setfunctions[request](self.received_setPVs[request])
        if result - self.received_setPVs[request] < 0.1:
            self.current_setPVs[request] = result
            self.epicsMatches.put("YES")
        else:
            self.current_setPVs[request] = self.received_setPVs[request]
            self.epicsMatches.put("YES")
            print("RF result differs from EPICS value.")
            print("result", result, "Epics value", self.received_setPVs[request])
            self.epicsMatches.put("NO")


if __name__ == "__main__":
    rfb = RFBackend("Beamline:RF", 0, 6, 0, 5)
