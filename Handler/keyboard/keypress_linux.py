import sys

from Handler.keyboard.keypress import KeyPressesHandler
import Config.conf as conf

class KeyPressHandlerLinux(KeyPressesHandler):
  def __init__(self, func) -> None:
    super().__init__(func)
    
  def run(self, func) -> chr:
        x = 0
        while x != conf.END_PROGRAM:
            try:
                print("Waiting input!")
                x = sys.stdin.read(1)[0]
                print(x)
                # do something based on press
                func(x)
            except BaseException as e:
                self.exc = e
                x = conf.END_PROGRAM
                func(x)
                
  def join(self) -> None:
      return super().join()