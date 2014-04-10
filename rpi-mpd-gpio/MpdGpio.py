import RPi.GPIO as GPIO
import socket
from mpd import MPDClient, ConnectionError
from Timer import Timer
from Screen import Screen

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
self.status.mpd =
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
self.status.song =
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
    ''' Constants. Don't change! '''
    STATE_STARTUP = 0;
    STATE_NORMAL = 1;
    
    mpd = None
    screen = None
    timer = None
    status = dict()
    observers = []
    timer = None
    
    # Constructor
    def __init__(self):
        # Set state
        self.status['state'] = self.STATE_STARTUP
        
        # Setup MPD client
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
        self.screen.onStatusChange()
        
        print(self.getIpAddress())
        
        # Start timer
        self.timer = Timer()
        self.timer.addRepeatingTask(POLLING_INTERVAL, self.updateMpdStatus)
        #self.timer.addRepeatingTask(SCREEN_UPDATE_INTERVAL, self.screen.tick)
        self.timer.start()
        
    # Getters
    ''' Get the GPIO interface '''
    def getGPIO(self):
        return self.GPIO  
    
    def getStatus(self):
        return self.status      
    
    ''' Get the current IP address or None if it doesn't have one '''
    def getIpAddress(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('google.com', 0))
            return s.getsockname()[0]
        except Error as e:
            return None
    
    # Methods
    ''' Add a state observer to the list of observers. The observer had to have an onStatusChange() callback '''
    def addObserver(self, observer):
        self.observers.append(observer)
    
    ''' Notify the observers that the status has changed '''
    def notifyObservers(self):
        for observer in self.observers:
            observer.onStatusChange()
        
    def updateMpdStatus(self):
        done = False
        while not done:
            try:
                self.status['mpd'] = self.mpd.status()
                self.status['song'] = self.mpd.currentsong()
                if self.status['state'] == self.STATE_STARTUP:
                    self.status['state'] = self.STATE_NORMAL
                self.notifyObservers()
                done = True
                #print(str(self.status))
                #print(str(self.song))
            except ConnectionError as e:
                print(str(e))
                self.mpdConnect()
            
    def mpdConnect(self):
        self.mpd.connect(MPD_ADDRESS, MPD_PORT)         
    
    def pauseOrPlay(self, channel):
        if 'state' in self.status['mpd']:
            if self.status['mpd']['state'] == 'play':
                try:
                    self.mpd.pause(1)
                    self.status['mpd']['state'] = 'pause'
                    print('Pause')
                except: pass
            else:
                try: 
                    self.mpd.pause(0)
                    self.status['mpd']['state'] = 'play'
                    print('Play')
                except: pass
            self.notifyObservers()
        
    def volumeUp(self, channel):
        if 'volume' in self.status:
            try:
                vol = int(self.status['mpd']['volume'])
            except:
                vol = 0
                
            if vol < 100:
                try:
                    self.mpd.setvol(vol + 1)
                    self.status['mpd']['volume'] = str(vol+1)
                    self.notifyObservers()
                    print('Volume Down: ' + str(vol + 1))
                except: pass # Sometimes ProtocolError occurs
        
    def volumeDown(self, channel):
        if 'volume' in self.status:
            try:
                vol = int(self.status['mpd']['volume'])
            except:
                vol = 100
               
            if vol > 0:
                try:
                    self.mpd.setvol(vol - 1)
                    self.status['mpd']['volume'] = str(vol-1)
                    self.notifyObservers()
                    print('Volume Down: ' + str(vol - 1))
                except: pass # Sometimes ProtocolError occurs   
            
mpdgpio = MpdGpio()
        