from threading import Thread
import pyaudio

import Config.conf as conf

class AudioFilter():
        def __init__(self, dig_filter) -> None:
                self.filter = dig_filter
        
        @staticmethod
        def __clamp_output(data):
                data = int(data)

                if data > conf.MAX_AUDIO_VALUES:
                        return conf.MAX_AUDIO_VALUES
                
                if data < conf.MIN_AUDIO_VALUES:
                        return conf.MIN_AUDIO_VALUES
                
                return data
        
        @staticmethod
        def __convert_bytes_to_array(item) -> list[int]:
            # convert bytes stream into integer
            temp : bytes

            n = pyaudio.get_sample_size(conf.FORMAT) # sample bytes size
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
        def __convert_arr_to_bytes(data_arr):
            byte_data = b''
            for data in data_arr:
                temp = data.to_bytes(2, 'little', signed=True)
                byte_data += temp 
            return byte_data 
        
        def increase_volume(self, data):
            return data * 10 ** (20 / conf.GAIN)
          
        def filter_audio(self, raw_data : bytes):
                data_arr = self.__convert_bytes_to_array(raw_data)
                filtered_data = self.filter.filter(data_arr)
                gain_data = map(lambda x:self.increase_volume(x), filtered_data)
                rounded_data = map(lambda x: self.__clamp_output(x), gain_data)
                return self.__convert_arr_to_bytes(rounded_data)
                # return raw_data

class Player():         
    def __init__(self, buffer, audio_filter) -> None:
        self.__thread = Thread(target = self.run)
        self.__driver = pyaudio.PyAudio()
        self.stream = None
        self.buffer = buffer
        self.exc = None
        self.__thread.start()
        self.filter = audio_filter
        # self.internal_buffer = []

    def run(self):
        try:
            # open a stream
            self.stream = self.__driver.open(format=conf.FORMAT, channels=conf.CHANNELS, 
                        rate=conf.RATE, output=True, frames_per_buffer=conf.CHUNK)

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
    
    @classmethod 
    def init_player(cls, records, audio_filter):
        player = cls(records, audio_filter)
        return player