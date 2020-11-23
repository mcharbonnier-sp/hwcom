from abc import ABC, abstractmethod
from potable.saveable import Saveable


class CollectingData(Exception):
    """ Exception raised if the connection is waiting for data.
    """

    def __init__(self, msg, cmd_args, *args: object) -> None:
        super().__init__(msg, *args)
        self.command_args = cmd_args


class ErrorResponse(Exception):
    pass


class Protocol(ABC, Saveable):
    @classmethod
    def class_path(cls):
        return 'Protocol'

    @abstractmethod
    def flush(self):
        """ Flush internal buffers

        :return:
        """
        pass

    @abstractmethod
    def make_query(self, *args) -> bytes:
        """
        :rtype: bytes
        :return: The data to send
        """
        pass

    @abstractmethod
    def make_set_command(self, *args) -> bytes:
        """
        :rtype: bytes
        :return: The data to send
        """
        pass

    @abstractmethod
    def add_new_data_bytes(self, data: bytes):
        """ Adds the latest data bytes received from the transport layer to the internal buffer.

        :param bytes data:
        :return:
        """

    @abstractmethod
    def get_response(self, cmd_args):
        """
        :param: Any cmd_args
        :rtype: object
        :return: modified response
        """
        pass

    def log_command(self, command, cmd_args):
        """
        :param str command: The command that has been sent
        :param cmd_args: The parameters used to build the command
        :return: The command, or shorter for logging purpose.
        """
        return command

    def clean_answer(self, response, cmd_args):
        """
        :param response: The response obtained from getResponse
        :param cmd_args: The parameter from the query that returned this response.
        :return: The simpified answer
        """
        return response