from multiprocessing import Queue

from Filter.DigitalFilter.FilterDesigner import FIR_FilterDesigner
from libs.Include.fft_iterative import convfft
from recorder.recorder import *

if __name__ == "__main__":
        fp = [3400, 8000]
        fs = [1400, 10400]
        Fs = Recorder.RATE     
        filter_type = "bandpass"
        fir_filter_designer = FIR_FilterDesigner(f_p=fs, f_s=fp, A_p=3, A_s=20, Fs=Fs, filter_type=filter_type)
        fir_filter = fir_filter_designer.create_filter()
        
        fir_filter.init_filter(1024)
        audio_filter = AudioFilter(fir_filter)

        records = Queue(maxsize=100)
        t_ = init_recorder(records)
        t__ = init_player(records, audio_filter)

        for thread in t_:
                thread.join()
        
        t__.join()


