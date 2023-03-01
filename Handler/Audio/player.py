from threading import Thread
import traceback

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
          
        def filter_audio(self, raw_datas : list[bytes]):
            output_chunks = []
            data0, data1 = map(lambda x: self.__convert_bytes_to_array(x), raw_datas)
            filtered_data = self.filter.filter(data0, data1)
            
            for result in filtered_data:
                gain_data = map(lambda x:self.increase_volume(x), result)
                rounded_data = map(lambda x: self.__clamp_output(x), gain_data)
                output_chunks.append(self.__convert_arr_to_bytes(rounded_data))
                
            return output_chunks

class Player():         
    def __init__(self, buffer, audio_filter) -> None:
        self.__thread = Thread(target = self.run, daemon="True")
        self.__driver = pyaudio.PyAudio()
        self.stream = None
        self.buffer = buffer
        self.exc = None
        self.__thread.start()
        self.filter = audio_filter
        self.internal_buffer = [] # to store two chunks of data

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
                self.internal_buffer.append(data)
                
                if len(self.internal_buffer) == 2:
                    filtered_data = self.filter.filter_audio(self.internal_buffer)
                    for audio_data in filtered_data:
                        self.stream.write(audio_data)
                    
                    self.internal_buffer = []

            self.stream.close()
            print("Player terminated!")

        except BaseException as e:
            print(traceback.format_exc())
            print("Error in Player: {}".format(e))
            self.stream.close()
            self.exc = e
    
    def join(self) -> None:
        self.__thread.join()
        if self.exc != None:
            raise self.exc
        
    def is_active(self):
        return self.__thread.is_alive()
    
    @classmethod 
    def init_player(cls, records, audio_filter):
        player = cls(records, audio_filter)
        return player