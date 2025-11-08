import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

MAX_WORKERS = 0

try:
    import os

    MAX_WORKERS = len(os.sched_getaffinity(0)) * 2
except:
    MAX_WORKERS = cpu_count() * 2

MAX_WORKERS = max(8, MAX_WORKERS)


class EarthFMThreadExecutor:
    _thread = None
    _running_tasks = {}

    def __init__(self):
        # print(f"[MoonThread]: USING {MAX_WORKERS} THREADS")
        self._thread = ThreadPoolExecutor(MAX_WORKERS)

    def function_wrapper(self, function_, fname, args):
        tid = threading.get_ident()
        self._running_tasks[tid] = fname
        start = time.time()
        try:
            function_(*args)
        except Exception as e:
            # print(f"\n[MoonThread ERROR] {fname}: {e}")
            print(traceback.format_exc())
        finally:
            duration = time.time() - start
            if duration > 5.0:
                pass
                # print(f"[MoonThread WARNING] {fname} ran for {duration:.2f}s")
            # else:
            # print(f"[MoonThread] {fname} completed in {duration:.2f}s")
            self._running_tasks.pop(tid, None)

    def submit(self, function_, *args):
        fname = getattr(function_, "__name__", str(function_))
        # print(f"[MoonThread] Submitting: {fname}({', '.join(map(str, args[:2]))}...)")
        self._thread.submit(self.function_wrapper, function_, fname, args)

    def print_active_tasks(self, *args):
        if not self._running_tasks:
            # print("[MoonThread] No active tasks.")
            return
        # print("[MoonThread] Active Tasks:")
        for tid, fname in dict(self._running_tasks).items():
            print(f" - Thread ID {tid}: {fname}")
