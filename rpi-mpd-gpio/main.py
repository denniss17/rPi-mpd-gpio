import RPi.GPIO as GPIO
import socket
from mpd import MPDClient, ConnectionError
from Timer import Timer
from Screen import *

''' MPD settings '''
MPD_ADDRESS = "localhost"
MPD_PORT = 6600

''' Pin numbers '''
PIN_PAUZE_PLAY = 19
PIN_VOLUME_UP = 21
PIN_VOLUME_DOWN = 23
PIN_LEFT = 24
PIN_RIGHT = 26
PIN_MENU = 12

''' Timing settings '''
POLLING_INTERVAL = 0.5 # Time (in s) between mpd status pollings
SCREEN_UPDATE_INTERVAL = 1 # Time (in s) between screen updates
BUTTON_BOUNCETIME = 200 # Time (in ms) as used for the software bouncetime of the pins

'''
Value examples
self.status =
{
    'songid': '260', 
    'playlistlength': '194', 
    'playlist': '365', 
    'repeat': '1', 
    'consume': '0', 
    'mixrampdb': '0.000000', 
    'random': '1', 
    'state': 'play', 
    'xfade': '0', 
    'volume': '100', 
    'single': '0', 
    'mixrampdelay': 'nan', 
    'nextsong': '189', 
    'time': '29:191', 
    'song': '66', 
    'elapsed': '28.688', 
    'bitrate': '192', 
    'nextsongid': '383', 
    'audio': '44100:24:2'
}
self.song =
{
    'album': 'All The Little Lights', 
    'artist': 'Passenger', 
    'track': '8/12', 
    'title': 'Patient Love', 
    'pos': '66', 
    'last-modified': '2013-12-05T20:42:34Z', 
    'disc': '1/2', 
    'file': 'USB/MUSIC/Passenger - Patient Love.mp3', 
    'time': '191', 
    'date': '2013', 
    'genre': 'Folk', 
    'id': '260'
}
'''


class MpdGpio:
    mpd = None
    screen = None
    timer = None
    status = None
    song = None
    timer = None
    
    def __init__(self):
        self.mpd = MPDClient()
        self.mpd.timeout = 10  # network timeout in seconds (floats allowed), default: None
        self.mpd.idletimeout = None
        
        # Setup GPIO
        self.GPIO = GPIO
        self.GPIO.setwarnings(False)
        self.GPIO.setmode(GPIO.BOARD)
        
         # Add button callbacks
        GPIO.setup(PIN_PAUZE_PLAY, GPIO.IN)
        GPIO.setup(PIN_VOLUME_UP, GPIO.IN)
        GPIO.setup(PIN_VOLUME_DOWN, GPIO.IN)
        GPIO.add_event_detect(PIN_PAUZE_PLAY, GPIO.RISING, callback=self.pauseOrPlay, bouncetime=BUTTON_BOUNCETIME)
        GPIO.add_event_detect(PIN_VOLUME_UP, GPIO.RISING, callback=self.volumeUp, bouncetime=BUTTON_BOUNCETIME)
        GPIO.add_event_detect(PIN_VOLUME_DOWN, GPIO.RISING, callback=self.volumeDown, bouncetime=BUTTON_BOUNCETIME)
        
        # Start LCD
        self.screen = Screen(self)
        print(self.getIpAddress())
        
        # Start timer
        self.timer = Timer()
        self.timer.addRepeatingTask(POLLING_INTERVAL, self.mpdUpdateStatus)
        self.timer.addRepeatingTask(SCREEN_UPDATE_INTERVAL, self.screen.tick)
        self.timer.start()
        
        
    def getGPIO(self):
        return self.GPIO
        
    def getIpAddress(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('google.com', 0))
            return s.getsockname()[0]
        except Error as e:
            return None
    
    def mpdConnect(self):
        self.mpd.connect(MPD_ADDRESS, MPD_PORT)
        
    def mpdUpdateStatus(self):
        done = False
        while not done:
            try:
                self.status = self.mpd.status()
                self.song = self.mpd.currentsong()
                if self.screen.getState() == STATE_STARTUP:
                    self.screen.setState(STATE_NORMAL)
                done = True
                #print(str(self.status))
                #print(str(self.song))
            except ConnectionError as e:
                print(str(e))
                self.mpdConnect()
            
                
    
    
    def pauseOrPlay(self, channel):
        if 'state' in self.status:
            if self.status['state'] == 'play':
                self.mpd.pause(1)
                self.screen.setState(STATE_PAUSE)
                print('Pause')
            else:
                self.mpd.pause(0)
                self.screen.setState(STATE_NORMAL)
                print('Play')
        
    def volumeUp(self, channel):
        if 'volume' in self.status:
            try:
                vol = int(self.status['volume'])
            except:
                vol = 0
                
            if vol < 100:
                self.mpd.setvol(vol + 1)
            print('Volume Up: ' + str(vol + 1))
        
    def volumeDown(self, channel):
        if 'volume' in self.status:
            try:
                vol = int(self.status['volume'])
            except:
                vol = 100
                
            if vol > 0:
                self.mpd.setvol(vol - 1)
            print('Volume Down: ' + str(vol - 1))
            
mpdgpio = MpdGpio()
        