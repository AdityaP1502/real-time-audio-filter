from time import sleep
from pynput import keyboard
from win32gui import GetWindowText, GetForegroundWindow
from threading import Thread

class KeyPressHandlerWindows():
    end_key = keyboard.Key.esc
    
    def __init__(self, func) -> None:
        self.exc = None
        self.is_paused=False  # pause keylog listener
        self.is_closed=False  # stop and close keylog
        self.l=None  # listener

        self.listened_window=GetWindowText(GetForegroundWindow())  # set listened window name
        self.focused_checker=Thread(target=self.check_focused, daemon="True")  # check if out of focused window in a thread
        self.focused_checker.start()
        
        self.__func = self.on_press_factory(func)
        self.start()
      
    def join(self):
        self.is_closed=True
        self.stop()
        if self.exc != None:
          raise self.exc

    def on_press_factory(self, func):
      def on_press(key):
        try:
          a = func(key)
          if a == False:
            return False
        except Exception as e:
          self.exc=e
          self.is_closed=True
          return False
      
      return on_press
    
    def start(self):
        self.l=keyboard.Listener(on_press=self.__func)
        self.l.start()
        
    def stop(self):
        if self.l:
          # stop listener
          self.l.stop()
          self.l.join()
        
    def check_focused(self):
        while not self.is_closed:
            if GetWindowText(GetForegroundWindow())!=self.listened_window:  # compare now focused window with listened window
                if not self.is_paused:  # if different and not paused, stop listening
                    self.stop()
                    self.is_paused=True
            elif self.is_paused:  # if same but paused, restart listening
                    self.start()
                    self.is_paused=False
            sleep(0.1)
    
    def is_active(self):
        return self.__thread.is_alive()