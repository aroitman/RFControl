import ctypes
import os


# Define switch class to interface with the dll
class RFSwitch:
    def __init__(self, PortNumber, COMNumber):
        self.libpath = os.path.abspath("COM-HVAMX4ED.dll")
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

    def setup(self, config_number=None):
        if config_number is None:
            print(self.get_config_list()[-1])
            while True:
                try:
                    config_number = int(input("Select a config number from the dictionary above:"))
                    break
                except ValueError:
                    print("Invalid input. Try again")
        print("Loading config number", config_number, "...")
        self.load_current_config(config_number)
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
