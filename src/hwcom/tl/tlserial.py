import serial

from ..transportlayer import TransportLayer


class SerialTL(TransportLayer):
    def __init__(self, address='COM0', baudrate=9600, parity=serial.PARITY_NONE, stop_bits=serial.STOPBITS_ONE,
                 bytesize=serial.EIGHTBITS, timeout=0.01):
        super().__init__()
        self.address = address
        self.baudrate = baudrate
        self.parity = parity
        self.stop_bits = stop_bits
        self.bytesize = bytesize
        self.timeout = timeout
        self._port = None

    @classmethod
    def name(cls) -> str:
        return 'Serial'

    def open(self):
        self._port = serial.Serial(port=self.address, baudrate=self.baudrate, parity=self.parity,
                                   stopbits=self.stop_bits, bytesize=self.bytesize, timeout=self.timeout)

    def close(self):
        self._port.close()
        self._port = None

    def send(self, message: bytes):
        self._port.write(message)

    def recv(self):
        return self._port.read(30)

    def flush(self):
        self._port.flushInput()


SerialTL.register_class()
