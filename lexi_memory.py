import json
import os
from threading import Lock

class LexiMemoryStore:
    """Simple thread-safe persistent memory store for Lexi."""
    def __init__(self, path: str = "output/lexi_memory.json"):
        self.path = path
        self._lock = Lock()
        if not os.path.exists(path):
            with open(path, "w") as f:
                json.dump({}, f)

    def load(self):
        with self._lock:
            with open(self.path, "r") as f:
                return json.load(f)

    def save(self, data: dict):
        with self._lock:
            with open(self.path, "w") as f:
                json.dump(data, f, indent=2)

    def get(self, key: str, default=None):
        mem = self.load()
        return mem.get(key, default)

    def set(self, key: str, value):
        mem = self.load()
        mem[key] = value
        self.save(mem)

    def clear(self):
        self.save({})
