from client import ToolRetryBackoff

attempt = [0]
def unstable_network_call():
    attempt[0] += 1
    if attempt[0] < 3:
        raise ConnectionResetError("Remote server closed connection")
    return {"status": "ok", "attempts": attempt[0]}

breaker = ToolRetryBackoff(max_retries=3, base_delay=0.05, failure_threshold=5)
result = breaker.execute_with_retry(unstable_network_call)
print("Successful Result:", result)
