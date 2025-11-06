# hyperx/core/worker.py
import threading, queue
from hyperx.logger.hx_logger import *
_logger = load_logger("hyperx.worker")
_logger.info("Worker thread initialized")


class WorkerThread(threading.Thread):
    def __init__(self, task_queue):
        super().__init__(daemon=True)
        self.task_queue = task_queue

    def run(self):
        while True:
            func, args, kwargs = self.task_queue.get()
            try:
                func(*args, **kwargs)
                logger.debug(f"[Worker] executed {func.__name__}")
            except Exception as e:
                logger.error(f"[Worker] failed {func.__name__}: {e}")
            self.task_queue.task_done()

# Shared queue and bootstrap
tasks = queue.Queue()
worker = WorkerThread(tasks)
worker.start()
