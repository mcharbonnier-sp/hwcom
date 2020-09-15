from collections import deque

from protocol import Protocol, CollectingData


class TextProtocol(Protocol):
    def __init__(self) -> None:
        super().__init__()
        self.ans_termination = b'\n'
        self.cmd_termination = self.ans_termination
        self.encoding = 'utf8'
        self.read_buffer = deque()
        self.incomplete_message = b''

    def flush(self):
        self.read_buffer.clear()
        self.incomplete_message = b''

    def make_query(self, cmd: str) -> bytes:
        return cmd.encode(self.encoding) + self.cmd_termination

    def make_set_command(self, cmd: str) -> bytes:
        return cmd.encode(self.encoding) + self.cmd_termination

    def add_new_data_bytes(self, data: bytes):
        self.incomplete_message += data
        if self.ans_termination in self.incomplete_message:
            elements = self.incomplete_message.split(self.ans_termination)
            self.incomplete_message = elements[-1]
            self.read_buffer.extend(elements[0:-1])

    def get_response(self, cmd_args) -> str:
        if self.read_buffer:
            return self.read_buffer.popleft().decode(self.encoding).strip()
        else:
            raise CollectingData('No or incomplete answer, Collecting data...')
