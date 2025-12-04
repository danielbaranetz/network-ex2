# client.py
import argparse, socket, json, sys


HOST = "127.0.0.1"
PORT = 5555
def request(host: str, port: int, payload: dict) -> dict:
    """Send a single JSON-line request and return a single JSON-line response."""
    try:
        data = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
        with socket.create_connection((host, port), timeout=5) as s:
            s.sendall(data)
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
        return {"ok": False, "error": str(e)}
    return {"ok": False, "error": "No response"}
def main():
    expressions = ["5*5+9", "3*(5+4)", "6/2+9", "Create your own expression"]

    while True:
        try:
            print("\n--------------------------------")
            options = int(input("Choose mode:\n1. Calc (Math)\n2. GPT (Text Prompt)\n3. Exit\nYour choice: "))
        except ValueError:
            print("Please enter a number.")
            continue
        if options == 3:
            print("Exiting...")
            break
        payload = None
        if options == 1:
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
            payload = {
                "mode": "calc",
                "data": {"expr": selected_expr},
                "options": {"cache": True}
            }
            if payload:
                print(f"Sending request: {payload}")
                resp = request(HOST, PORT, payload)

                print("\nServer Response:")
                print(json.dumps(resp, ensure_ascii=False, indent=2))

        if options == 2:
            query = input("Please enter prompt to query Chat-GPT: ")
            payload = {
                "mode": "gpt",
                "data": {"prompt": query},
                "options": {"cache": True}
            }
            if payload:
                print(f"Sending request: {payload}")
                resp = request(HOST, PORT, payload)

                print("\nServer Response:")
                print(json.dumps(resp, ensure_ascii=False, indent=2))


    # if args.mode == "calc":
    #     if not args.expr:
    #         print("Missing --expr", file=sys.stderr); sys.exit(2)
    #     payload = {"mode": "calc", "data": {"expr": args.expr}, "options": {"cache": not args.no_cache}}
    # else:
    #     if not args.prompt:
    #         print("Missing --prompt", file=sys.stderr); sys.exit(2)
    #     payload = {"mode": "gpt", "data": {"prompt": args.prompt}, "options": {"cache": not args.no_cache}}
    #
    # resp = request(args.host, args.port, payload)
    # print(json.dumps(resp, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
