import platform
import pyaudio

# user system
PLATFORM = platform.system()

# Audio config files
RATE = 44100 # in Hz
CHUNK = 2048 # number of samples per block
RECORD_SECONDS = 5 # only used when in blocking mode
FORMAT = pyaudio.paInt16 # 16 bit per sample
MAX_AUDIO_VALUES = 32767
MIN_AUDIO_VALUES = -32768
CHANNELS = 1 # number of audio channels
GAIN = 100 # in db

# keyboard event
START_RECORDING = 'v'
END_PROGRAM = chr(27) # esc


