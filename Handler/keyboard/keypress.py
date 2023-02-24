from threading import Thread

class KeyPressesHandler():
    def __init__(self, func) -> None:
        self.__thread = Thread(target=self.run, args=(func, ))
        self.exc = None
        self.__thread.start()

    def run(self, func) -> chr:
        NotImplemented

    def join(self) -> None:
        self.__thread.join()
        if self.exc != None:
            raise self.exc
            