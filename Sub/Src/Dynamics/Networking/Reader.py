import io

class Reader:
    '''
    The reader class is meant to read messages (duh).
    '''
    def __init__(self, message, buffer = None):
        if buffer is None:
            self._buffer = io.BytesIO(message)
        else:
            self._buffer = buffer
        self._list = []
        self._byteArray = None

    def read(self, size = None):
        self._byteArray = self._buffer.read(size)
        #while True:
            #print(byteArray)
        return self._byteArray

    def readAll(self):
        #while True:
            #print(self._buffer.getvalue())
        return self._buffer.getvalue()

    def read_from_file(self, file):
        with open(file, "br") as f:
            for line in f:
                self.list.append(line)
        return self._list

    #def seek(self, message):
