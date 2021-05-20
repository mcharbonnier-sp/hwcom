import logging
from collections import deque
import socket
from typing import Optional

from potable.saveable import State

from ..transportlayer import TransportLayer


class IpTransportLayer(TransportLayer):
    def __init__(self, address=None):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.level = logging.ERROR
        if address is None:
            address = ('192.168.0.2', )
        self.address = address
        self.socket: Optional[socket.socket] = None
        self.read_buffer = deque()

    def is_open(self):
        return self.socket is not None

    def _check_socket(self):
        if self.socket is None:
            raise ConnectionError('Socket is not open')

    def get_state(self) -> State:
        state = super().get_state()
        state.add_parameter('address', ','.join([self.address[0], str(self.address[1])]))
        return state

    def set_state(self, state: State):
        super().set_state(state)
        address_str = state.get_parameters()['address'].split(',')
        self.address = address_str[0], int(address_str[1])

    @classmethod
    def class_path(cls):
        return 'TCP-IP'

    def open(self):
        self.logger.info('Connecting to address %s', self.address)
        if self.socket is not None:
            self.logger.info('Connection failed, a connection is already opened.')
            return
        self.socket = socket.socket()
        self.socket.settimeout(0.1)
        try:
            self.socket.connect(self.address)
        except:
            self.socket = None
            self.logger.exception('Connection Failed')
            raise
        self.logger.info('Connected')

    def close(self):
        self._check_socket()
        self.socket.close()
        self.socket = None
        self.logger.info('Connection closed.')

    def send(self, message):
        self._check_socket()
        self.logger.info('Sending %s', message)
        self.socket.send(message)

    def recv(self):
        self._check_socket()
        try:
            return self.socket.recv(1024)
        except socket.timeout:
            return b''

    def flush(self):
        self._check_socket()
        pass


IpTransportLayer.register_class()
