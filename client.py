"""Agentic Tool Call Retry & Circuit Breaker.
100% Python Standard Library.
"""

import time

class ToolRetryBackoff:
    """Manages retry backoff and circuit breaking for unreliable tool execution."""
    def __init__(self, max_retries=3, base_delay=0.1, failure_threshold=2):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.circuit_open = False

    def execute_with_retry(self, fn, *args, **kwargs):
        if self.circuit_open:
            raise RuntimeError("Circuit breaker is OPEN. Fast failing tool call.")
        attempts = 0
        while attempts <= self.max_retries:
            try:
                res = fn(*args, **kwargs)
                self.failure_count = 0
                return res
            except Exception as e:
                attempts += 1
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    self.circuit_open = True
                if attempts > self.max_retries:
                    raise e
                delay = self.base_delay * (2 ** (attempts - 1))
                time.sleep(delay)
