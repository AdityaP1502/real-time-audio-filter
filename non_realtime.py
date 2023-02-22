import sys

import wave
import pyaudio

from recorder.recorder import Recorder
from Filter.DigitalFilter.FilterDesigner import FIR_FilterDesigner
from libs.Include.fft_iterative import convfft

MAX_INT16 = 32767
MIN_INT16 = -32768

def save_to_wav(data, name="output.wav"):
    print(len(data))
    wf = wave.open(name, "wb")
    wf.setnchannels(Recorder.CHANNELS)
    wf.setsampwidth(pyaudio.get_sample_size(Recorder.FORMAT))
    wf.setframerate(Recorder.RATE)
    wf.writeframes(data)
    wf.close()

def save_filtered(data, filter):
    global MAX_INT16, MIN_INT16
    def clamp_output(data):
                data = int(data)

                if data > MAX_INT16:
                        return MAX_INT16
                
                if data < MIN_INT16:
                        return MIN_INT16
                
                return data
                
    data_arr = Recorder.convert_bytes_to_array(data)
    print(len(data_arr))
    xm = [data_arr[1024 * i:1024 * (i + 1)] for i in range(len(data_arr) // 1024)]
    print(len(xm))
    filtered_data_bytes = b""
    for xn in xm:
        filtered_data = filter.filter(xn)
        rounded_data = map(lambda x: clamp_output(x), filtered_data)
        data = Recorder.convert_arr_to_bytes(rounded_data)
        filtered_data_bytes += data 


    print(len(filtered_data_bytes))
    # filtered_data = filter.filter(data_arr)
    save_to_wav(filtered_data_bytes, "output_filtered.wav")
    

if __name__ == "__main__":
    assert len(sys.argv) > 1, "Specified mode operation"
    if sys.argv[1].upper() == "RECORD":
        data = Recorder.blocking_record()
        save_to_wav(data)

    else:
        fp = [2000]
        fs = [3000]
        Fs = Recorder.RATE 
        filter_type = "highpass"
        fir_filter_designer = FIR_FilterDesigner(f_p=fs, f_s=fp, A_p=3, A_s=20, Fs=Fs, filter_type=filter_type)
        fir_filter = fir_filter_designer.create_filter()
        fir_filter.showFreqResponse()
        fir_filter.init_filter(1024)

        wf = wave.open("output.wav", "rb")

        length = wf.getnframes()
        print(length)
        data = wf.readframes(length)

        save_filtered(data, fir_filter)


