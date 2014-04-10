from LCD import LCD
from threading import Lock

TEXT_START = 'Starting...'
TEXT_PAUSE = '|| Pause        '
TEXT_NO_SONG = 'No song playing!'

ERROR_NO_MPD_STATE = 'E: No MPD state'

class Screen:
    """ Mainly the 'view' of this application. Controls the LCD """
    mpdgpio = None
    lock = None
    substate = 0
    currentStatus = None
    lcd = None
    
    def __init__(self, mpdgpio):
        self.lock = Lock()
        self.mpdgpio = mpdgpio
        self.mpdgpio.addObserver(self)
        self.GPIO = self.mpdgpio.getGPIO()
        # Use other layout (GPIO.BOARD, so pin number change)
        self.lcd = LCD(pin_rs=22, pin_e=18, pins_db=[16, 11, 13, 15], GPIO=self.GPIO)
        #self.lcd = LCD(GPIO=self.GPIO)
        self.lcd.begin(16,2)
        
    def onStatusChange(self):
        print('onStatusChange')
        self.tick()
        self.currentStatus = self.mpdgpio.getStatus()
        
    def padString(self, string):
        return string + ((16-len(string)) * ' ')
    
    ''' Format a number of seconds to a time string (ex: 115 becomes "1:55") '''
    def toTime(self, number):
        return '%d:%02d' % (int(float(number)) / 60, int(float(number)) % 60)
        
    def tick(self):
        print('tick')
        # Use lock to avoid concurrent modification
        # Because the state can change in another thread (button callback thread)
        self.lock.acquire()
        try:
            if self.mpdgpio.getStatus()['state']==self.mpdgpio.STATE_STARTUP:
                self.tickStartup()
            elif self.mpdgpio.getStatus()['state']==self.mpdgpio.STATE_NORMAL:
                self.tickNormal()
        finally:
            self.lock.release()
            
    def tickStartup(self):
        if self.currentStatus != None and self.currentStatus['state'] != STATE_STARTUP:
            self.lcd.clear()
            self.lcd.message(TEXT_START)
                
    def tickNormal(self):
        status = self.mpdgpio.getStatus()
        if 'song' not in self.currentStatus or self.currentStatus['song'] != status['song']:
            # New song
            # COULD BE NONE!
            self.lcd.clear()
            self.substate = 0
            
        if 'mpd' not in status or 'state' not in status['mpd']:
            self.lcd.message(ERROR_NO_MPD_STATE)
            return
        
        if status['song'] != None and 'artist' in status['song'] and 'title' in status['song']:
            # Yay! there is a song playing :)
            self.lcd.setCursor(0,0)
            if self.substate==0:
                # Show artist
                self.lcd.message(self.padString(status['song']['artist'][:16]))
            elif self.substate==4:
                # Show title
                self.lcd.message(self.padString(status['song']['title'][:16]))
            self.substate = (self.substate + 1) % 8
                
            # Show progress on second line
            self.lcd.setCursor(2,1)
            if 'elapsed' in status['mpd'] and 'time' in status['song']:
                self.lcd.message('%-7s%7s' % (self.toTime(status['mpd']['elapsed']), self.toTime(status['song']['time'])))
        else:
            # No song currently playing
            self.lcd.message(TEXT_NO_SONG)
            
        if status['mpd']['state'] == 'stop':
            self.lcd.setCursor(0,1)
            self.lcd.message('S')
        elif status['mpd']['state'] == 'pause':
            self.lcd.setCursor(0,1)
            self.lcd.message('P')
        elif status['mpd']['state'] == 'play':
            self.lcd.setCursor(0,1)
            self.lcd.message('>') 
       
        
       #if status['mpd']['state'] == 'stop':
       #     self.lcd.setCursor(0,0)
       #     self.lcd.message(TEXT_NO_SONG)
       # elif status['mpd']['state'] == 'pause':
       #     self.lcd.setCursor(0,0)
       #     self.lcd.message(TEXT_PAUSE)
       # elif status['mpd']['state'] == 'play':
       #     if status['song'] != None and 'artist' in status['song'] and 'title' in status['song']:
       #         # Yay! there is a song playing :)
       #         self.lcd.setCursor(0,0)
       #         if self.substate==0:
       #             # Show artist
       #             self.lcd.message(self.padString(status['song']['artist'][:16]))
       #         elif self.substate==2:
       #             # Show title
       #             self.lcd.message(self.padString(status['song']['title'][:16]))
       #         self.substate = (self.substate + 1) % 4
       #             
       #         # Show progress on second line
       #         self.lcd.setCursor(0,1)
       #         if 'elapsed' in status['mpd'] and 'time' in status['song']:
       #             self.lcd.message('%-8s%8s' % (self.toTime(status['mpd']['elapsed']), self.toTime(status['song']['time'])))
       #     else:
       #         # No song currently playing
       #         self.lcd.message(TEXT_NO_SONG)
       # '''
       # #self.lcd.message('.........0.........1.........2.........3.........4.........5.........6.........7')
       #if 'artist' in self.mpdgpio.song and 'title' in self.mpdgpio.song:
        #    self.lcd.message((self.mpdgpio.song['artist'] + '-' + self.mpdgpio.song['title'])[:40])
           # pass
        #self.lcd.clear()
        #self.lcd.setCursor(0,0);
        #if 'artist' in self.mpdgpio.song:
        #    self.lcd.message(self.mpdgpio.song['artist'])
        #elf.lcd.setCursor(0,1);
        #f 'title' in self.mpdgpio.song:
        #    self.lcd.message(self.mpdgpio.song['title'])