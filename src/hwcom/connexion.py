import logging
import time
from enum import Enum
from threading import Event

from potable.saveable import Saveable

from .protocol import Protocol, CollectingData
from .transportlayer import TransportLayer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CommunicationAborted(Exception):
    pass


class CommandType(Enum):
    COMMAND = 0
    QUERY = 1


class Connexion(Saveable):
    """
    Asynchronous connexion.
      * Set and Query will raise the CollectingData exception until the response is obtained.
      * If CollectingData is raised, poll_set_finished and poll_query_response must be called until
        CollectingData is not raised anymore.
    """
    def __init__(self, transport_layer: TransportLayer, protocol: Protocol, timeout=1, stop: Event = None):
        """
        :param TransportLayer transport_layer: Transport layer to use.
        :param Protocol protocol: the protocol used to build queries and manage answers
        """
        self.transport_layer = transport_layer
        self.protocol = protocol
        self.logger = logger
        self.timeout = timeout
        self.timeout_start_time = 0
        if stop is None:
            self.stop = Event()
        else:
            self.stop = stop

    def open(self):
        self.transport_layer.open()
        self.protocol.flush()

    def close(self):
        self.transport_layer.close()

    def _send(self, command: bytes, command_type: CommandType):
        """
        :param bytes command: The command to send
        :param CommandType command_type: The type of the command (T_COMMAND, T_QUERY)
        """
        self.logger.debug('Sending: %s', command)
        self.transport_layer.send(command)
        self.timeout_start_time = time.time()

    # noinspection PyMethodMayBeStatic
    def _receive(self, command_params):
        """
        :param list[str] command_params: Query elements
        :rtype: bytes
        :return: Received Data
        """
        ans = self.transport_layer.recv()
        self.logger.debug('Receiving: %s', ans)
        return ans

    def set(self, command_params):
        """
        Send a command to the hardware, no answer is returned to the main program. Only errors are checked.
        :param command_params:
        :raises CollectingData
        :return:
        """
        command = self.protocol.make_set_command(command_params)
        self._send(command, CommandType.COMMAND)
        raise CollectingData('Command sent', command_params)

    def poll_set_finished(self, command_params):
        """ Raises CollectingData until a response to the set() command is obtained.

        :param command_params:
        :return:
        """
        self.receive_check_error(command_params)

    def receive_check_error(self, cmd_args):
        new_data_bytes = self._receive(cmd_args)

        if len(new_data_bytes) > 0:
            self.timeout_start_time = time.time()
        elif time.time() - self.timeout_start_time > self.timeout:
            raise TimeoutError()

        self.protocol.add_new_data_bytes(new_data_bytes)

        try:
            response = self.protocol.get_response(cmd_args)
        except CollectingData:
            raise
        except Exception as ec:
            logger.warning('{}\n'
                           'with protocol "{}\n"'
                           'Query: {}\n'.format(ec, self.protocol.__class__.__name__, cmd_args))
            raise
        return response

    def set_sync(self, cmd_args, poll_delay=0.1):
        command = self.protocol.make_set_command(cmd_args)
        self._send(command, CommandType.COMMAND)
        while True:
            try:
                self.poll_set_finished(cmd_args)
            except CollectingData:
                if self.stop.wait(poll_delay):
                    raise CommunicationAborted()
            else:
                return

    def query(self, cmd_args):
        """
        :param cmd_args: Query elements
        :raises CollectingData
        :return: query result
        """
        command = self.protocol.make_query(cmd_args)
        self._send(command, CommandType.QUERY)
        raise CollectingData('Query sent', cmd_args)

    def poll_query_response(self, query_args):
        """ Raises Collecting data until the response is obtained.
            :return: The response to the query.
        """
        return self.protocol.clean_answer(self.receive_check_error(query_args), query_args)

    def query_sync(self, query_args, poll_delay=0.1):
        command = self.protocol.make_query(query_args)
        self._send(command, CommandType.QUERY)
        while True:
            try:
                ans = self.poll_query_response(query_args)
            except CollectingData:
                if self.stop.wait(poll_delay):
                    raise CommunicationAborted()
            else:
                return ans


class ConnexionSync(Connexion):
    """ Synchronous connection, set and query will block until the response is received.
        Consequently, CollectingData is never raised.
    """
    def set(self, command_params):
        try:
            super().set(command_params)
        except CollectingData:
            pass
        self.receive_check_error(command_params)

    def query(self, cmd_args):
        try:
            super().query(cmd_args)
        except CollectingData:
            pass
        return self.protocol.clean_answer(self.receive_check_error(cmd_args), cmd_args)

    def set_sync(self, cmd_args, poll_delay=0.1):
        self.set(cmd_args)

    def query_sync(self, query_args, poll_delay=0.1):
        return self.query(query_args)

    def receive_check_error(self, cmd_args):
        while True:
            try:
                response = super().receive_check_error(cmd_args)
                break
            except CollectingData:
                pass
        return response
