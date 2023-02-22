import tty
import sys
import termios
from threading import Thread
from multiprocessing import Queue, Process
from typing import *
from time import time
import pyaudio

orig_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)

class AudioFilter():
        MAX_INT16 = 32767
        MIN_INT16 = -32768
        def __init__(self, dig_filter) -> None:
                self.filter = dig_filter
        
        def clamp_output(self, data):
                data = int(data)

                if data > self.MAX_INT16:
                        return self.MAX_INT16
                
                if data < self.MIN_INT16:
                        return self.MIN_INT16
                
                return data
                
        def filter_audio(self, raw_data : bytes):
                data_arr = Recorder.convert_bytes_to_array(raw_data)
                filtered_data = self.filter.filter(data_arr)
                rounded_data = map(lambda x: self.clamp_output(x), filtered_data)
                return Recorder.convert_arr_to_bytes(rounded_data)
                # return raw_data

class Recorder():
    WAVE_OUTPUT_FILENAME =  "output.wav"
    CHUNK : int = 1024
    FORMAT :  str = pyaudio.paInt16
    CHANNELS : int = 1
    RATE : int = 44100
    RECORD_SECONDS : int = 5

    def __init__(self, queue) -> None:
        self.__thread = Thread(target=self.run)
        self.state = 0
        self.__driver = pyaudio.PyAudio()
        self.stream = None
        self.buffer = queue
        self.data_id = 0
        self.exc = None
        self.__thread.start()

    def update_state(self, key_press):
        if key_press == "v":
            self.state = 1

        elif key_press == KeyPressesHandler.END_CHARACTER:
            for i in range(8):
                self.buffer.put(None)
            
            self.state = -1

    @staticmethod
    def blocking_record():
        # record for 5 seconds
        p = pyaudio.PyAudio()

        stream = p.open(format = Recorder.FORMAT, channels=Recorder.CHANNELS, 
                rate=Recorder.RATE, input=True, frames_per_buffer=Recorder.CHUNK)

        frames = []
        print("Recording*")
        for i in range(int(Recorder.RATE / Recorder.CHUNK * Recorder.RECORD_SECONDS)):
            data = stream.read(Recorder.CHUNK)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()

        print("Recording stopped!")
        return b''.join(frames)
        

    def run(self):
        while self.state != -1:
            try:
                while self.state == 1:
                    if self.stream == None:
                        print("Recording!")
                        self.stream = self.__driver.open(format = self.FORMAT, channels=self.CHANNELS, 
                            rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)

                    data = self.stream.read(self.CHUNK)
                    self.buffer.put([self.data_id, data])
                    self.data_id += 1


                if self.stream != None:
                    print("Recording Stopped!")
                    self.stream.stop_stream()
                    self.stream.close()
                    self.stream = None
                    self.data_id = 0

            except BaseException as e:
                self.stream.stop_stream()
                self.stream.close()
                self.__driver.close()
                self.exc = e
            

    @staticmethod
    def convert_bytes_to_array(item) -> list[int]:
        # convert bytes stream into integer
        temp : bytes

        n = pyaudio.get_sample_size(Recorder.FORMAT) # sample bytes size
        xn = [0 for i in range(len(item) // n)] # data in integer
        k = 0 

        for i in range(0, len(item), n):
          # get the data bytes
          temp = item[i:i + n]
          # convert to int
          xn[k] = int.from_bytes(temp, "little", signed = True)
          k += 1
        
        return xn

    @staticmethod
    def convert_arr_to_bytes(data_arr):
        byte_data = b''
        for data in data_arr:
            temp = data.to_bytes(2, 'little', signed=True)
            byte_data += temp 
        return byte_data

    def join(self):
        self.__thread.join()
        if self.exc != None:
            raise self.exc


class Player():
    __CHUNK : int = 1024
    __FORMAT :  str = pyaudio.paInt16
    __CHANNELS : int = 1
    __RATE : int = Recorder.RATE
         
    def __init__(self, buffer, audio_filter) -> None:
        self.__thread = Thread(target = self.run)
        self.__driver = pyaudio.PyAudio()
        self.stream = None
        self.buffer = buffer
        self.exc = None
        self.__thread.start()
        self.internal_buffer = []
        self.filter = audio_filter

    def run(self):
        try:
            # open a stream
            self.stream = self.__driver.open(format = self.__FORMAT, channels=self.__CHANNELS, 
                        rate=self.__RATE, output=True, frames_per_buffer=self.__CHUNK)

            print("Player up and running!")
            while True:
                buffer_data = self.buffer.get()
                if (buffer_data == None): break
                data_id, data = buffer_data
                # self.internal_buffer.append(item)
                # if (len(self.internal_buffer) == 100):
                #     while len(self.internal_buffer):
                #         data = self.internal_buffer.pop(0)
                #         self.stream.write(data)
                data = self.filter.filter_audio(data)

                self.stream.write(data)
                

            self.stream.close()
            print("Player terminated!")

        except BaseException as e:
            print(e)
            self.stream.close()
            self.exc = e
    
    def join(self) -> None:
        self.__thread.join()
        if self.exc != None:
            raise self.exc

class KeyPressesHandler():
    END_CHARACTER = chr(27) # esc

    def __init__(self, func) -> None:
        self.__thread = Thread(target=self.run, args=(func, ))
        self.exc = None
        self.__thread.start()

    
    def run(self, func) -> chr:
        x = 0
        while x != self.END_CHARACTER:
            try:
                print("Waiting input!")
                x = sys.stdin.read(1)[0]
                print(x)
                # do something based on press
                func(x)
            except BaseException as e:
                print(e)
                self.exc = e
                x = self.END_CHARACTER
                func(x)

    def join(self) -> None:
        self.__thread.join()
        if self.exc != None:
            raise self.exc

def consume(buffer, records, process_func):
    while True:
        item = buffer.get()
        # sentinel
        if (item == None): 
            records.put(None)
            break
    
        # unpack the data
        data_id, data = item

        # process item
        data = process_func(data)

        records.put(data)

    print("Done processing!")


def init_recorder(records):
    # for i in range(8):
    #   consumer = Process(target=consume, args=[buffer, records, consume_func, ])
    #   consumer.start()
    #   consumers.append(consumer)
    
    recorder = Recorder(records)
    keyhandler = KeyPressesHandler(func=recorder.update_state)

    return [keyhandler, recorder]

def init_player(records, audio_filter):
    player = Player(records, audio_filter)
    return player

if __name__ == "__main__":
    pass