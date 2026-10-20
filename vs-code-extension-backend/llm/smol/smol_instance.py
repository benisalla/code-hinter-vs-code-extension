import threading


class _LazySmol:
    """Singleton SmolLM that loads the weights on first use (not at import time),
    so the API, the tests and the offline tutor start without torch/transformers."""

    _instance = None
    _lock = threading.Lock()

    def load(self):
        if _LazySmol._instance is None:
            with _LazySmol._lock:
                if _LazySmol._instance is None:
                    from llm.smol.smol import SmolLM
                    _LazySmol._instance = SmolLM()
        return _LazySmol._instance

    def __getattr__(self, name):
        return getattr(self.load(), name)


# singleton instance of SmolLM
smol = _LazySmol()
