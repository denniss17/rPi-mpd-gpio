from LCD import LCD

STATE_STARTUP = 0;
STATE_NORMAL = 1;

class Screen:
    """ Mainly the 'view' of this application. Controls the LCD """
    mpdgpio = None
    state = None
    substate = None
    oldState = None
    displayedSong = None
    lcd = None
    
    def __init__(self, mpdgpio):
        self.mpdgpio = mpdgpio
        self.state = STATE_STARTUP
        self.lcd = LCD()
        self.lcd.begin(16,2)
        
    def setState(self, state):
        self.state = state
        
    def padString(self, string):
        return string + ((16-len(string)) * ' ')
    
    def toTime(self, number):
        return '%d:%02d' % (int(float(number)) / 60, int(float(number)) % 60)
        
    def tick(self):
        if self.state==STATE_STARTUP:
            self.tickStartup()
        elif self.state==STATE_NORMAL:
            self.tickNormal()
            
    def tickStartup(self):
        if self.oldState != STATE_STARTUP:
            self.lcd.clear()
            self.lcd.message('Starting...')
                
    def tickNormal(self):
        if self.displayedSong != self.mpdgpio.song:
            # New song
            self.displayedSong = self.mpdgpio.song
            # COULD BE NONE!
            self.lcd.clear()
            self.substate = 0
        
        if self.mpdgpio.song != None and 'artist' in self.mpdgpio.song and 'title' in self.mpdgpio.song:
            # Yay! there is a song playing :)
            self.lcd.setCursor(0,0)
            if self.substate==0:
                # Show artist
                self.lcd.message(self.padString(self.mpdgpio.song['artist'][:16]))
            elif self.substate==2:
                # Show title
                self.lcd.message(self.padString(self.mpdgpio.song['title'][:16]))
            self.substate = (self.substate + 1) % 4
                
            # Show progress on second line
            self.lcd.setCursor(0,1)
            if 'elapsed' in self.mpdgpio.status and 'time' in self.mpdgpio.song:
                self.lcd.message('%-8s%8s' % (self.toTime(self.mpdgpio.status['elapsed']), self.toTime(self.mpdgpio.song['time'])))
        else:
            # No song currently playing
            self.lcd.message('No song playing!')
        
        #self.lcd.message('.........0.........1.........2.........3.........4.........5.........6.........7')
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