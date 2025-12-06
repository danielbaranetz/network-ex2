import argparse, socket, json, sys


def send_request(sock: socket.socket, payload: dict) -> dict:
    try:
        data = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")

        sock.sendall(data)

        # waiting for a response
        buff = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:  # if server disconnect
                return {"ok": False, "error": "Server disconnected"}
            buff += chunk
            if b"\n" in buff:
                line, _, _ = buff.partition(b"\n")
                return json.loads(line.decode("utf-8"))
    except Exception as e:
        return {"ok": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5555)
    args = parser.parse_args()

    expressions = ["5*5+9", "3*(5+4)", "6/2+9", "Create your own expression"]

    print(f"Connecting to {args.host}:{args.port}...")

    try:
        with socket.create_connection((args.host, args.port)) as s: # opening the socket once
            print("Connected! Session is open.")

            while True:
                try:
                    print("\n--------------------------------")
                    options = int(
                        input("Choose mode:\n1. Calc (Math)\n2. Chat-GPT (Text Prompt)\n3. Exit\nYour choice: "))
                except ValueError:
                    print("Please enter a number.")
                    continue

                if options == 3:
                    print("Exiting...")
                    break  # exit

                payload = None

                if options == 1: # calculator option
                    print("\n--- Calculator Menu ---")
                    for i, n in enumerate(expressions):
                        print(f"{i + 1}. {n}")
                    try:
                        calc_option = int(input("Select an option: "))
                    except ValueError:
                        print("Invalid input")
                        continue

                    selected_expr = ""
                    if calc_option == len(expressions):
                        selected_expr = input("Enter your math expression: ")
                    elif 1 <= calc_option < len(expressions):
                        selected_expr = expressions[calc_option - 1]
                    else:
                        print("Invalid selection.")
                        continue

                    payload = {"mode": "calc", "data": {"expr": selected_expr}, "options": {"cache": True}}

                elif options == 2: # chatGPT option
                    query = input("Please enter prompt to query Chat-GPT: ")
                    payload = {"mode": "gpt", "data": {"prompt": query}, "options": {"cache": True}}

                if payload:
                    resp = send_request(s, payload)
                    print("\nServer Response:")
                    print(json.dumps(resp, ensure_ascii=False, indent=2))

                    if not resp.get("ok") and resp.get("error") == "Server disconnected":
                        print("Server closed connection.")
                        break

    except ConnectionRefusedError:
        print(f"Error: Could not connect to {args.host}:{args.port}. Is server running?")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()