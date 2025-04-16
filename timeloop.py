from threading import Thread, Event
import threading
import ctypes
import time
class timeoutexception(Exception):
    def __init__(self, msg):
        super().__init__(msg)

def minutestoseconds(minutes):
    return minutes*60

def hourstoseconds(hours):
    return minutestoseconds(hours*60)

def daystoseconds(days):
    return hourstoseconds(days*24)

class TimeoutTimer:
    def __init__(self):
        self._event = Event()
        self.thread = Thread

    def start(self, duration_seconds):
        self._event.clear()
        self.thread(target=lambda: (time.sleep(duration_seconds), self._event.set()),
               daemon=True).start()

    def timed_out(self):
        return self._event.is_set()

    def cancel(self):
        if self.thread and self.thread.is_alive():
            self._event.clear()
