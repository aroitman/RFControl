import ctypes


# Define power supply class to interface with the dll
class RFPS:
    def __init__(self, PortNumber, COMNumber, libpath):
        #self.libpath = os.path.abspath("COM-HVPSU2D.dll")
        self.libpath = libpath
        self.RFPS = ctypes.cdll.LoadLibrary(self.libpath)
        self.PortNumber = PortNumber  # port used for power supply, usually 0
        self.COMNumber = COMNumber  # COM port number, which depends on where PS is connected.

    # open and close ports
    def open(self):
        print("Opening Port", self.PortNumber)
        return self.RFPS.COM_HVPSU2D_Open(self.PortNumber, self.COMNumber)

    def close(self):
        print("Closing Port", self.PortNumber)
        return self.RFPS.COM_HVPSU2D_Close(self.PortNumber, self.COMNumber)

    # setup functions
    def get_interlock_enable(self):
        con_out = ctypes.pointer(ctypes.c_bool(0))
        con_BNC = ctypes.pointer(ctypes.c_bool(0))
        self.RFPS.COM_HVPSU2D_GetInterlockEnable(self.PortNumber, con_out, con_BNC)
        return (con_out.contents.value, con_BNC.contents.value)

    def set_interlock_enable(self, con_out, con_BNC):
        self.RFPS.COM_HVPSU2D_SetInterlockEnable(self.PortNumber, con_out, con_BNC)

    def get_PSU_full_range(self):
        PSU0 = ctypes.pointer(ctypes.c_bool(0))
        PSU1 = ctypes.pointer(ctypes.c_bool(0))
        self.RFPS.COM_HVPSU2D_GetPSUFullRange(self.PortNumber, PSU0, PSU1)
        return (PSU0.contents.value, PSU1.contents.value)

    def set_PSU_full_range(self, PSU0, PSU1):
        self.RFPS.COM_HVPSU2D_SetPSUFullRange(self.PortNumber, PSU0, PSU1)

    def get_device_enable(self):
        enable = ctypes.pointer(ctypes.c_bool(0))
        self.RFPS.COM_HVPSU2D_GetDeviceEnable(self.PortNumber, enable)
        return enable.contents.value

    def set_device_enable(self, enable):
        self.RFPS.COM_HVPSU2D_SetDeviceEnable(self.PortNumber, enable)

    def get_PSU_enable(self):
        PSU0 = ctypes.pointer(ctypes.c_bool(0))
        PSU1 = ctypes.pointer(ctypes.c_bool(0))
        self.RFPS.COM_HVPSU2D_GetPSUEnable(self.PortNumber, PSU0, PSU1)
        return (PSU0.contents.value, PSU1.contents.value)

    def set_PSU_enable(self, PSU0, PSU1):
        self.RFPS.COM_HVPSU2D_SetPSUEnable(self.PortNumber, PSU0, PSU1)

    # functions for controlling voltage and current
    def get_output_voltage(self, PSU):
        voltage = ctypes.pointer(ctypes.c_double(0))
        self.RFPS.COM_HVPSU2D_GetPSUOutputVoltage(self.PortNumber, PSU, voltage)
        return voltage.contents.value

    # sets current for both PSUs
    def set_output_voltage(self, voltage):
        voltage = ctypes.c_double(voltage)
        self.RFPS.COM_HVPSU2D_SetPSUOutputVoltage(self.PortNumber, 0, voltage)
        self.RFPS.COM_HVPSU2D_SetPSUOutputVoltage(self.PortNumber, 1, voltage)
        return self.get_output_voltage(0)

    def get_output_current(self, PSU):
        current = ctypes.pointer(ctypes.c_double(0))
        self.RFPS.COM_HVPSU2D_GetPSUOutputCurrent(self.PortNumber, PSU, current)
        return current.contents.value

    # sets current for both PSUs
    def set_output_current(self, current):
        current = ctypes.c_double(current)
        self.RFPS.COM_HVPSU2D_SetPSUOutputCurrent(self.PortNumber, 0, current)
        self.RFPS.COM_HVPSU2D_SetPSUOutputCurrent(self.PortNumber, 1, current)
        return self.get_output_current(0)

    def get_PSU_set_output_voltage(self, PSU):
        voltage_set = ctypes.pointer(ctypes.c_double(0))
        voltage_limit = ctypes.pointer(ctypes.c_double(0))
        self.RFPS.COM_HVPSU2D_GetPSUSetOutputVoltage(self.PortNumber, PSU, voltage_set, voltage_limit)
        return (voltage_set.contents.value, voltage_limit.contents.value)

    def get_PSU_set_output_current(self, PSU):
        current_set = ctypes.pointer(ctypes.c_double(0))
        current_limit = ctypes.pointer(ctypes.c_double(0))
        self.RFPS.COM_HVPSU2D_GetPSUSetOutputCurrent(self.PortNumber, PSU, current_set, current_limit)
        return (current_set.contents.value, current_limit.contents.value)

        # functions to set things up and shut things down. See lablog for details
    def setup(self):
        print("Disabling Interlock...")
        self.set_interlock_enable(False, False)
        print("Setting Full Range on PSUs...")
        self.set_PSU_full_range(True, True)
        print("Enabling Device...")
        self.set_device_enable(True)
        print("Enabling PSUs...")
        self.set_PSU_enable(True, True)
        print("Setup complete. Getting voltage and current Data...")
        print("PSU0 Voltage:", self.get_output_voltage(0), "V")
        print("PSU1 Voltage:", self.get_output_voltage(1), "V")
        print("PSU0 Current:", self.get_output_current(0), "A")
        print("PSU1 Current:", self.get_output_current(1), "A")
        print("PSU0 Voltage Limit:", self.get_PSU_set_output_voltage(0)[1], "V")
        print("PSU1 Voltage Limit:", self.get_PSU_set_output_voltage(1)[1], "V")
        print("PSU0 Current Limit:", self.get_PSU_set_output_current(0)[1], "A")
        print("PSU1 Current Limit:", self.get_PSU_set_output_current(1)[1], "A")

    def shutdown(self):
        print("Setting Current and Voltage to 0...")
        self.set_output_voltage(0.0)
        self.set_output_current(0.0)
        print("PSU0 Voltage:", self.get_output_voltage(0), "V")
        print("PSU1 Voltage:", self.get_output_voltage(1), "V")
        print("PSU0 Current:", self.get_output_current(0), "A")
        print("PSU1 Current:", self.get_output_current(1), "A")
        print("Disabling PSUs...")
        self.set_PSU_enable(False, False)
        print("Disabling Device...")
        self.set_device_enable(False)
        print("Disabling Full Range on PSUs...")
        self.set_PSU_full_range(False, False)
        print("Enabling Interlock...")
        self.set_interlock_enable(True, True)
        print("Shutdown complete.")


if __name__ == "__main__":
    ps = RFPS(0, 6)
    ps.open()
    ps.setup()
    ps.shutdown()
    ps.close()
