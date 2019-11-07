#----------------------------------------------------------------------
# Parameters to define
#----------------------------------------------------------------------
DATA_PATH = ''

AMP_NAME = None
AMP_SERIAL = None

# trigger device
TRIGGER_DEVICE = None # None | 'ARDUINO' | 'USB2LPT' | 'DESKTOP' | 'SOFTWARE'
TRIGGER_FILE = r''


STREAMBUFFER = 2                   # Stream buffer [sec]
WINDOWSIZE = 2                     # window length of acquired data when calling get_window [sec]

TIMER_SLEEP = 0.25*60

NJOBS = 8                          # For multicore PSD processing
