import sys
from threading import Thread
from typing import *
import pyaudio

import Config.conf as conf
from Handler.keyboard.keypress_windows import KeyPressHandlerWindows
from Handler.keyboard.keypress_linux import KeyPressHandlerLinux


class Recorder():
    def __init__(self, queue) -> None:
        self.__thread = Thread(target=self.run, daemon="True")
        self.state = 0
        self.__driver = pyaudio.PyAudio()
        self.stream = None
        self.buffer = queue
        self.data_id = 0
        self.exc = None
        self.__thread.start()

    def update_state(self, key_press):
        if key_press == conf.START_RECORDING:
            self.state = 1

        elif key_press == conf.END_PROGRAM and self.state == 0:            
            self.buffer.put(None)
            self.state = -1
            return False

        elif key_press == conf.END_RECORDING:
            self.state = 0

    def update_state_windows(self, key_press):
        if type(key_press).__name__ == "Key":
            if key_press == KeyPressHandlerWindows.end_key:
                key = chr(27)

            else:
                key = str(key_press)

        elif type(key_press).__name__ == "KeyCode":
            key = key_press.char
            if key == '\x03':
                print("CTRL + C is pressed. Aborting...")
                self.update_state(chr(27))  # end audio handler
                raise Exception("Ctrl + c is pressed")

        self.update_state(key)

    @staticmethod
    def blocking_record():
        # record for 5 seconds
        p = pyaudio.PyAudio()

        stream = p.open(format=conf.FORMAT, channels=conf.CHANNELS,
                        rate=conf.RATE, input=True, frames_per_buffer=conf.CHUNK)

        frames = []
        print("Recording*")
        for i in range(int(conf.RATE / conf.CHUNK * conf.RECORD_SECONDS)):
            data = stream.read(conf.CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()

        print("Recording stopped!")
        return b''.join(frames)

    def run(self):
        print("Recorder is up and running!")
        try:
            while self.state != -1:
                while self.state == 1:
                    if self.stream == None:
                        print("Recording!")
                        self.stream = self.__driver.open(format=conf.FORMAT, channels=conf.CHANNELS,
                                                         rate=conf.RATE, input=True, frames_per_buffer=conf.CHUNK)

                    data = self.stream.read(conf.CHUNK)
                    self.buffer.put([self.data_id, data])
                    self.data_id += 1

                if self.stream != None:
                    print("Recording Stopped!")
                    self.stream.stop_stream()
                    self.stream.close()
                    self.stream = None
                    self.data_id = 0

            print("Recorder is closed")

        except BaseException as e:
            self.stream.stop_stream()
            self.stream.close()
            self.__driver.close()
            self.exc = e
            self.buffer.put(None)

    def join(self):
        self.__thread.join()
        if self.exc != None:
            raise self.exc

    def is_active(self):
        return self.__thread.is_alive()

    @classmethod
    def init_recorder(cls, records):
        # for i in range(8):
        #   consumer = Process(target=consume, args=[buffer, records, consume_func, ])
        #   consumer.start()
        #   consumers.append(consumer)

        recorder = cls(records)

        if conf.PLATFORM == "Windows":
            keyhandler = KeyPressHandlerWindows(
                func=recorder.update_state_windows)

        else:
            keyhandler = KeyPressHandlerLinux(func=recorder.update_state)

        return [keyhandler, recorder]
