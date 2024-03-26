import ctypes


# Define switch class to interface with the dll
class RFSwitch:
    def __init__(self, PortNumber, COMNumber, libpath):
        #self.libpath = os.path.abspath("COM-HVAMX4ED.dll")
        self.libpath = libpath 
        self.RFSwitch = ctypes.cdll.LoadLibrary(self.libpath)  # load library
        self.PortNumber = PortNumber  # port used for RF switch, usually 0
        self.COMNumber = COMNumber  # COM port number, which depends on where switch is connected.

    # open and close ports
    def open(self):
        print("Opening Port", self.PortNumber)
        self.RFSwitch.COM_HVAMX4ED_Open(self.PortNumber, self.COMNumber)

    def close(self):
        print("Closing Port", self.PortNumber)
        self.RFSwitch.COM_HVAMX4ED_Close(self.PortNumber, self.COMNumber)

    # config functions
    def load_current_config(self, config_number):
        self.RFSwitch.COM_HVAMX4ED_LoadCurrentConfig(self.PortNumber, config_number - 1)

    # see whether the switch is on or off, 7 means on, 0 means off.
    def get_controller_state(self):
        state = ctypes.pointer(ctypes.c_byte(0))
        self.RFSwitch.COM_HVAMX4ED_GetControllerState(self.PortNumber, state)
        return state.contents.value

    # set controller state above.
    def set_controller_config(self, config):
        self.RFSwitch.COM_HVAMX4ED_SetControllerConfig(self.PortNumber, config)
        return self.get_controller_state()

    # get list of configuration file names and numbers
    def get_config_list(self):
        activetype = ctypes.c_bool * 126
        validtype = ctypes.c_bool * 126
        active = activetype()
        valid = validtype()
        self.RFSwitch.COM_HVAMX4ED_GetConfigList(self.PortNumber, active, valid)
        active_list = [i for i in active]
        valid_list = [i for i in valid]
        active_nums = [i + 1 for i in range(len(active_list)) if active_list[i] is True]
        valid_nums = [i + 1 for i in range(len(valid_list)) if valid_list[i] is True]
        config_name_dict = {}
        for num in valid_nums:
            name = ctypes.create_string_buffer(52)
            self.RFSwitch.COM_HVAMX4ED_GetConfigName(self.PortNumber, num - 1, name)
            name = str(name.raw).split('\\x00')[0]
            name = name.split("b'")[-1]
            config_name_dict[num] = name
        return (active_nums, valid_nums, config_name_dict)

    def get_oscillator_frequency(self):
        # get oscillator frequency in MHz
        period = ctypes.pointer(ctypes.c_int(0))
        self.RFSwitch.COM_HVAMX4ED_GetOscillatorPeriod(self.PortNumber, period)
        # convert period to proper format and then to frequency
        period = period.contents.value + 2
        freq = 100 / period
        return freq

    def set_oscillator_frequency(self, freq):
        # set oscillator frequency in MHz, and do the other steps in the lablog
        # convert frequency to period into units of 10 ns
        period = round(100 / freq)
        # subtract two for proper input format
        period_minus_two = period - 2
        period_minus_two = ctypes.c_int(period_minus_two)
        self.RFSwitch.COM_HVAMX4ED_SetOscillatorPeriod(self.PortNumber, period_minus_two)
        # set pulserwidth to be half of period, set it to pulser 0
        width_minus_two = round(period / 2) - 2
        width_minus_two = ctypes.c_int(width_minus_two)
        pulserno = 0
        self.RFSwitch.COM_HVAMX4ED_SetPulserWidth(self.PortNumber, pulserno, width_minus_two)
        # set switch trigger and enable config for switch 0.
        # In hexadecimal, 10 = 0A, 32 = 20
        self.RFSwitch.COM_HVAMX4ED_SetSwitchTriggerConfig(self.PortNumber, 0, 10)
        self.RFSwitch.COM_HVAMX4ED_SetSwitchEnableConfig(self.PortNumber, 0, 32)
        # set switch trigger and enable config for switch 1
        # In hexadecimal, 42 = 2A, 32 = 20
        self.RFSwitch.COM_HVAMX4ED_SetSwitchTriggerConfig(self.PortNumber, 1, 42)
        self.RFSwitch.COM_HVAMX4ED_SetSwitchEnableConfig(self.PortNumber, 1, 32)

        return self.get_oscillator_frequency()

    def setup(self):
        print("Enabling Controller...")
        self.set_controller_config(7)
        print("Controller state set to", self.get_controller_state())
        print("Setup complete")

    def shutdown(self):
        print("Disabling Controller...")
        self.set_controller_config(0)
        print("Controller state set to", self.get_controller_state())
        print("Shutdown complete")


if __name__ == "__main__":
    ps = RFSwitch(0, 5)
    ps.open()
    ps.setup(2)
    ps.shutdown()
    ps.close()
