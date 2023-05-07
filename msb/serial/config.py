from msb.config.MSBConfig import MSBConf


class SerialConf(MSBConf):
    regex: str = "(\\d*\\.?\\d+)kW\\s*(\\d*\\.?\\d+)rpm\\s*(\\d*\\.?\\d+)rpm\\s*(\\d*\\.?\\d+)m/s\\s*(-?\\d*\\.*\\d*)"
    device: str = "/usb/TTY0"
    topic: str = "imu"
    timeout: float = 0.05
    baudrate: int = 9600
    
