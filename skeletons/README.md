# 🚀 TCP Client-Server-Proxy Application

An Application-Layer networking project implementing a custom JSON-based protocol over TCP.
The system features a **Smart Caching Proxy**, **Persistent Connections**, and **GPT integration**.

---

## 🌟 Key Features

### 1. Robust Server (`server.py`)
* **Safe Calculator:** Evaluates mathematical expressions using a secure AST parser (no `eval()`).
* **GPT Integration:** Supports both a "Stub" mode and real OpenAI API calls via `.env`.
* **LRU Cache:** Internal caching mechanism to store recent results.
* **Persistent Connections:** Handles multiple requests over a single TCP connection.

### 2. Smart Proxy (`proxy.py`)
* **Application-Layer Parsing:** Fully parses JSON requests instead of just piping bytes.
* **Local Caching:** Checks its own LRU cache before forwarding requests to the server.
* **Traffic Reduction:** Reduces load on the main server by serving cached responses immediately (`proxy_cache: true`).
* **Resilience:** Can serve cached answers even if the main server is down.

### 3. Interactive Client (`client.py`)
* **Menu-Driven UI:** Easy-to-use interface for Math and GPT modes.
* **Persistent Session:** Opens one socket and keeps it alive for multiple requests.
* **Flexible:** Can connect directly to the Server or via the Proxy.

---

## 🛠️ Installation & Setup

1.  **Install Dependencies** (Required for GPT & Environment variables):
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure API Key:**
    * The API key already configured
---

## 🏃‍♂️ How to Run

You will need **3 separate terminal windows** to see the full system in action.

### Step 1: Start the Real Server
Listens on port `5555` by default.
```bash
python server.py
```
### Step 2: Start the Proxy server
Listens on port `5554` and forwarding to port `5555` by default.
```bash
python proxy.py
```
### Step 3: Start the Client.
Connect directly to server by default using port `5555`
Use --port `5554` to Connect to the Proxy server.
```bash
python client.py --port 5554
```

## 📂 Project Structure

* `server.py` - Main TCP server logic (Math evaluation & GPT integration).
* `client.py` - interactive client with menu and persistent connection support.
* `proxy.py` - Smart Application-Layer proxy with LRU Caching.
* `requirements.txt` - Python dependencies (OpenAI, Dotenv).
* `.env` - Configuration file for API Keys.

---

## 👨‍💻 Authors
#### Daniel Baranetz, Shaked Horesh
Submitted as part of Computer Networks Course (2025).