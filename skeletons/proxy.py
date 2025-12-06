# proxy.py
import argparse, socket, threading, json, time, collections


# cache class
class LRUCache:
    """Minimal LRU cache based on OrderedDict."""
    def __init__(self, capacity: int = 128):
        self.capacity = capacity
        self._d = collections.OrderedDict()

    def get(self, key):
        if key not in self._d:
            return None
        self._d.move_to_end(key)
        return self._d[key]

    def set(self, key, value):
        self._d[key] = value
        self._d.move_to_end(key)
        if len(self._d) > self.capacity:
            self._d.popitem(last=False)


#
def fetch_from_real_server(host, port, payload):
    """
    Connects to the real server, sends the request, gets the response, and closes.
    This is used when we have a Cache MISS.
    """
    try:
        # opening a socket to server for any request that is not in cache
        with socket.create_connection((host, port), timeout=5) as s:
            data = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
            s.sendall(data)

            # reading response from server
            buff = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buff += chunk
                if b"\n" in buff:
                    line, _, _ = buff.partition(b"\n")
                    return json.loads(line.decode("utf-8"))
    except Exception as e:
        return {"ok": False, "error": f"Upstream error: {e}"}
    return {"ok": False, "error": "No response from upstream"}


def handle_client(conn, server_host, server_port, cache):
    """
    Handles a persistent client connection (similar to server.py).
    Checks cache -> if miss -> fetch from real server -> save to cache -> return.
    """
    with conn:
        try:
            raw = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                raw += chunk

                # handling persistent connection
                while b"\n" in raw:
                    line, _, rest = raw.partition(b"\n")
                    raw = rest

                    try:
                        # unpack json
                        req = json.loads(line.decode("utf-8"))

                        # unique key for cache
                        cache_key = json.dumps(req, sort_keys=True)

                        # check cache (Cache Hit)
                        cached_resp = cache.get(cache_key)

                        if cached_resp:
                            print(f"[Proxy] Cache HIT for {req}")
                            # response from the proxy cache
                            if "meta" in cached_resp:
                                cached_resp["meta"]["proxy_cache"] = True
                            resp = cached_resp
                        else:
                            # no response in cache so sending to the server
                            print(f"[Proxy] Cache MISS for {req} -> Forwarding to {server_host}:{server_port}")
                            resp = fetch_from_real_server(server_host, server_port, req)

                            # saving in cache if response was ok(and not error)
                            if resp.get("ok"):
                                cache.set(cache_key, resp)

                        # responding to the client
                        out = (json.dumps(resp, ensure_ascii=False) + "\n").encode("utf-8")
                        conn.sendall(out)

                    except json.JSONDecodeError:
                        error_resp = {"ok": False, "error": "Invalid JSON"}
                        conn.sendall((json.dumps(error_resp) + "\n").encode("utf-8"))

        except Exception as e:
            print(f"[Proxy] Connection error: {e}")


# --- 4. Main Loop ---
def main():
    ap = argparse.ArgumentParser(description="Smart Caching TCP Proxy")
    ap.add_argument("--listen-host", default="127.0.0.1")
    ap.add_argument("--listen-port", type=int, default=5554)
    ap.add_argument("--server-host", default="127.0.0.1")
    ap.add_argument("--server-port", type=int, default=5555)
    args = ap.parse_args()

    cache = LRUCache(capacity=100)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((args.listen_host, args.listen_port))
        s.listen(16)
        print(
            f"[Proxy] Listening on {args.listen_host}:{args.listen_port} -> Forwarding to {args.server_host}:{args.server_port}")

        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, args.server_host, args.server_port, cache),
                                 daemon=True)
            t.start()


if __name__ == "__main__":
    main()