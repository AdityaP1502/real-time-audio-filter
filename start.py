from multiprocessing import Queue
import signal
from Tools.Filter.DigitalFilter.FilterDesigner import FIR_FilterDesigner
from Handler.Audio.recorder import *
from Handler.Audio.player import *
from Handler.keyboard.keyboard_interrupt import create_interupt_handler
import Config.conf as conf

if __name__ == "__main__":
    if conf.PLATFORM == "Linux":
        import tty
        import termios
        orig_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin)

    # filter design
    fp = [3400, 8000]
    fs = [1400, 10400]
    Fs = conf.RATE
    filter_type = "bandpass"
    fir_filter_designer = FIR_FilterDesigner(
        f_p=fs, f_s=fp, A_p=3, A_s=20, Fs=Fs, filter_type=filter_type)
    
    fir_filter = fir_filter_designer.create_filter()
    fir_filter.init_filter(1024)
    
    audio_filter = AudioFilter(fir_filter)
    
    records = Queue(maxsize=100)
    keyhandler, recorder = Recorder.init_recorder(records)
    player = Player.init_player(records, audio_filter)
    
    signal.signal(signal.SIGINT, create_interupt_handler(recorder))
    
    try:
        player.join()
        recorder.join()
        keyhandler.join()   
        
    except BaseException as e:
        sys.exit(1)
        
    finally:
        if conf.PLATFORM == "Linux":
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
            