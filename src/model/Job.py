import random, string
from concurrent.futures import Future

class Job:
    id_length = 8

    def __init__(self, url: str, webloc_filepath: str, options: str, future: Future, callback: callable):
        self.id = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(self.id_length))
        self.url = url
        self.webloc_filepath = webloc_filepath
        self.options = options
        self._future = future
        self.callback = callback
        future.add_done_callback(self.done_callback)
    
    def cancel(self) -> bool:
        return self._future.cancel()
    
    def get_status(self) -> str:
        if self._future.running(): return "downloading"
        elif self._future.cancelled(): return "cancelled"
        elif self._future.done() and self._future.exception() == None: return "completed"
        elif self._future.done() and self._future.exception() != None: return "failed"
        else: return "pending"

    def get_filename(self) -> str:
        raise NotImplementedError

    def done_callback(self, future: Future):
        success = future.done() and future.exception() == None
        self.callback(success, self.url, self.webloc_filepath)