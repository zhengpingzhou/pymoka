from datetime import datetime

class Timer(object):

    def __init__(self):
        self.start_time = datetime.now()

    def tic(self):
        self.time = datetime.now()
        return self

    def toc(self):
        now = datetime.now()
        delta = (now - self.time).total_seconds()
        wall = (now - self.start_time).total_seconds()
        print(f'Time delta: {delta}s, Wall time: {wall}s')
        self.time = now
        return self
