from typing import Optional

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
        self._port: Optional[serial.Serial] = None

    @classmethod
    def name(cls) -> str:
        return 'Serial'

    def open(self):
        self._port = serial.Serial(port=self.address, baudrate=self.baudrate, parity=self.parity,
                                   stopbits=self.stop_bits, bytesize=self.bytesize, timeout=self.timeout)

    def is_open(self):
        return self._port is not None

    def _check_port(self):
        if self._port is None:
            raise ConnectionError('Port is not open')

    def close(self):
        self._check_port()
        self._port.close()
        self._port = None

    def send(self, message: bytes):
        self._check_port()
        self._port.write(message)

    def recv(self):
        self._check_port()
        return self._port.read(30)

    def flush(self):
        self._check_port()
        self._port.flushInput()


SerialTL.register_class()
