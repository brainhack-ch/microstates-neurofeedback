#----------------------------------------------------------------------
# Parameters to define
#----------------------------------------------------------------------
DATA_PATH = r'C:\Users\brainhacker\Desktop\nd_data'

AMP_NAME = None
AMP_SERIAL = None

# trigger device
TRIGGER_DEVICE = None # None | 'ARDUINO' | 'USB2LPT' | 'DESKTOP' | 'SOFTWARE'
TRIGGER_FILE =  r'C:\Users\brainhacker\git\NeuroDecode\neurodecode\triggers\triggerdef_16'


STREAMBUFFER = 2                   	# Stream buffer [sec]
WINDOWSIZE = 2                     	# window length of acquired data when calling get_window [sec]

GLOBAL_TIME = 5*60					# [secs]
TIMER_SLEEP = 0.25*60				# [secs]

NJOBS = 8                          	# For multicore PSD processing
