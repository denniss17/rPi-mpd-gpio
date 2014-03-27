import sched, time

class Timer:
    s = None
    
    def __init__(self):
        self.s = sched.scheduler(time.time, time.sleep)
        
    def start(self):
        self.s.run()
        
    def addTask(self, delay, function, args=()):
        self.s.enter(delay, 1, function, args)
        
    def addRepeatingTask(self, interval, function, args=()):
        self.s.enter(0, 1, self._tick, (interval, function, args))
        
    def _tick(self, interval, function, args):
        self.s.enter(interval, 1, self._tick, (interval, function, args))
        function(*args)
        