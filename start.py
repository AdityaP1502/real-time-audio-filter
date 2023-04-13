from multiprocessing import Queue

from Handler.Audio.recorder import *
from Handler.Audio.player import *
from Tools.Filter.DigitalFilter.FilterDesigner import FIR_FilterDesigner
import Config.conf as conf

if __name__ == "__main__":
    if conf.PLATFORM == "Linux":
        import tty
        import termios
        orig_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin)

    # filter design
    fp = [8000, 16000]
    fs = [5000, 19000]
    Fs = conf.RATE
    filter_type = "bandpass"
    fir_filter_designer = FIR_FilterDesigner(
        f_p=fs, f_s=fp, A_p=3, A_s=20, Fs=Fs, filter_type=filter_type)
    
    fir_filter = fir_filter_designer.create_filter()
    fir_filter.init_filter(conf.CHUNK)
    
    audio_filter = AudioFilter(fir_filter)
    
    records = Queue(maxsize=100)
    keyhandler, recorder = Recorder.init_recorder(records)
    player = Player.init_player(records, audio_filter)
    
    try:
        player.join()
        recorder.join()
        keyhandler.join()
        print("All thread has finished without errors")
        
    except BaseException as e:
        print("Error while processing")
        
    finally:
        if conf.PLATFORM == "Linux":
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
   