from time import sleep
from pynput import keyboard
from win32gui import GetWindowText, GetForegroundWindow
from threading import Thread

class KeyPressHandlerWindows():
    end_key = keyboard.Key.esc
    
    def __init__(self, func) -> None:
        self.is_paused=False  # pause keylog listener
        self.is_closed=False  # stop and close keylog
        self.l=None  # listener

        self.listened_window=GetWindowText(GetForegroundWindow())  # set listened window name
        self.focused_checker=Thread(target=self.check_focused)  # check if out of focused window in a thread
        self.focused_checker.start()
        
        self.__func = func
        self.start()

    def join(self):
        # stop and close keylog
        self.is_closed=True
        self.stop()

    def start(self):
        self.l=keyboard.Listener(on_press=self.__func)
        self.l.start()
        
    def stop(self):
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