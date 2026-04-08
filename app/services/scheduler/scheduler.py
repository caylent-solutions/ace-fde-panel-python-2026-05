import time
import threading
from typing import Callable, Optional


class IntervalScheduler:
    def __init__(self, db=None):
        self.db = db
        self._jobs = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def add_job(self, name: str, func: Callable, interval_seconds):
        if func is None:
            return
        self._jobs[name] = {"func": func, "interval": interval_seconds, "last_run": 0}

    def remove_job(self, name):
        self._jobs.pop(name, None)

    def _run_loop(self):
        while self._running:
            now = time.time()
            for name, job in list(self._jobs.items()):
                if now - job["last_run"] >= job["interval"]:
                    try:
                        job["func"]()
                    except Exception as e:
                        print(f"job {name} failed: {e}")
                    job["last_run"] = now
            time.sleep(1)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

    def list_jobs(self):
        return list(self._jobs.keys())
