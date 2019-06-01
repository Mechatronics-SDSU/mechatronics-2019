import io

class Writer:
    '''
    This might come as a shock, but we use the writer class to write messages.
    '''
    def __init__(self, message, buffer = None):
        if buffer is None:
            self._buffer = io.BytesIO(message)
        else:
            self._buffer = buffer

    def write(self, message = None):
        if message is None:
            message = self._buffer.getvalue()
        with self._buffer as f:
            f.write(message)

    def write_to_file(self, file, message = None):
        if message is None:
            message = self._message
        with open(file,"bw") as f:
            f.write(message)
