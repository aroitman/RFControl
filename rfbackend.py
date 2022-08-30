from queue import Queue  # manage requests
from epics import PV  # allows access to EPICS variables

# dummy mode for testing
mode = "dummy"
if mode == "real":
    import rfps
    import rfswitch


class RFBackend:
    def __init__(self, name, PSPortNumber, PSCOMNumber, SWPortNumber, SWCOMNumber, config_number=2):
        # initialize ps wrapper
        self.PSPortNumber = PSPortNumber
        self.PSCOMNumber = PSCOMNumber
        self.SWPortNumber = SWPortNumber
        self.SWCOMNumber = SWCOMNumber
        self.config_number = config_number
        if mode == "real":
            # initialize PS wrapper
            self.rfps = rfps.RFPS(self.PSPortNumber, self.PSCOMNumber)
            self.rfps.setup()

            # initialize switch wrapper
            self.rfswitch = rfswitch.RFSwitch(self.SWPortNumber, self.SWCOMNumber)
            self.rfswitch.setup(self.config_number)

        # Initialize EPICS set PVs as dictionary
        self.setPVs = {"V": PV(name + ":setVoltage"), "I": PV(name + ":setCurrent"), "PS": PV(name + ":setPSState"), "SW": PV(name + ":setSWState")}
        # set function dictionary to make setting variables easier
        self.setfunctions = {"V": self.rfps.set_output_voltage, "I": self.rfps.set_output_current, "PS": self.ps_change_state, "SW": self.rfswitch.set_controller_config}
        # received and current PV dict to check the epics value with the rf value
        self.received_setPVs = {"V": None, "I": None, "PS": None, "SW": None}
        self.current_setPVs = {"V": None, "I": None, "PS": None, "SW": None}

        # Initialize EPICS get PVs as dictionary (PVs read from RF switch and ps)
        self.getPVs = {"V": PV(name + ":getVoltage"), "I": PV(name + ":getCurrent"), "SW": PV(name + ":getSWState"), "Vlim": PV(name + ":getVoltageLimit"), "Ilim": PV(name + ":getCurrentLimit"), "ilock": PV(name + ":getInterlock"), "FR": PV(name + ":getFullRange"), "PS": PV(name + ":getPSUState")}

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

        # put a read command into the Queue
        self.sendQueue.put("read")
        self.run()

    def run(self):
        while True:
            if self.sendQueue.qsize() <= self.maxSendBufferLength:
                self.sendQueue.put("read")

            request = self.sendQueue.get()
            if request == "read":
                if mode == "real":
                    self.read()
                else:
                    for key in self.getPVs:
                        self.getPVs[key].put(0)
            else:
                if mode == "real":
                    self.set_value(request)
                else:
                    self.epicsMatches.put("YES")
                    print("Currently in dummy mode. Set variables changed. Request received:", request)

    def read(self):
        self.getPVs["V"].put(self.rfps.get_output_voltage(0))
        self.getPVs["I"].put(self.rfps.get_output_current(0))
        self.getPVs["SW"].put(self.rfswitch.get_controller_state())
        self.getPVs["Vlim"].put(self.get_PSU_set_output_voltage(0)[1])
        self.getPVs["Ilim"].put(self.get_PSU_set_output_current(0)[1])

        # sets following variables to True if and only if results of the rfps functions are (True, True), otherwise, return False.
        self.getPVs["PS"].put(min(self.rfps.get_PSU_enable()))
        self.getPVs["ilock"].put(min(self.rfps.get_interlock_enable()))
        self.getPVs["FR"].put(min(self.rfps.get_PSU_full_range()))

    def setVChanged(self, **kw):
        self.sendQueue.put("V")

    def setIChanged(self, **kw):
        self.sendQueue.put("I")

    def setPSChanged(self, **kw):
        self.sendQueue.put("PS")

    def setSWChanged(self, **kw):
        self.sendQueue.put("SW")

    # helper function to change ps state
    def ps_change_state(self, state):
        if state == 1:
            self.rfps.setup()
            return 1
        else:
            self.rfps.shutdown()
            return 0

    # function to safely set variables
    def set_value(self, request):
        self.received_setPVs[request] = self.setPVs[request].get()
        if (self.epicsRunning.get() is None) or (self.epicsRunning.get() == 0):
            print("Connection to EPICS server lost")
        result = self.setfunctions[request](self.received_setPVs[request])
        if result == self.received_setPVs[request]:
            self.current_setPVs[request] = result
            self.epicsMatches.put("YES")
        else:
            print("RF result differs from EPICS value.")
            self.epicsMatches.put("NO")


if __name__ == "__main__":
    rfb = RFBackend("Beamline:RF", 0, 6, 0, 5)
