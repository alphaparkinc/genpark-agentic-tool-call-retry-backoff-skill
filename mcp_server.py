import sys
import json
from client import ToolRetryBackoff

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-agentic-tool-call-retry-backoff-skill", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "simulate_retry_execution",
                        "description": "Simulate tool retry with exponential backoff",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "simulated_failures": {"type": "integer", "default": 1}
                            }
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        args = params.get("arguments", {})
        fails = args.get("simulated_failures", 1)
        count = [0]
        def call_target():
            count[0] += 1
            if count[0] <= fails:
                raise IOError("Simulated IO failure")
            return "recovered"

        breaker = ToolRetryBackoff(max_retries=fails + 1, base_delay=0.01)
        res = breaker.execute_with_retry(call_target)
        return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps({"status": res, "total_attempts": count[0]})}]}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
