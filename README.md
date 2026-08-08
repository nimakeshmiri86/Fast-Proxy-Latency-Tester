# ⚡ Fast Proxy Latency Tester & Parser

A high-performance, multithreaded Python tool designed to evaluate and measure TCP connection latencies for various proxy configurations (VLESS, VMess, Trojan, and plain IP:Port).

### 🎯 Overview
In modern network architectures, selecting the most optimal routing node with minimum latency is crucial for maintaining performance. This tool concurrently parses proxy protocols, calculates real-time TCP handshake latency, and sorts the nodes to extract the fastest available configuration.

### ✨ Key Features
* **Multi-Protocol Parsing:** Automatically extracts host and port details from `vless://`, `vmess://` (Base64 JSON decoding), `trojan://`, and raw `IP:Port` formats.
* **Subscription Support:** Capable of decoding Base64-encoded subscription file strings directly.
* **Concurrent Execution:** Utilizes Python's `concurrent.futures.ThreadPoolExecutor` for high-speed parallel testing across hundreds of nodes.
* **Flexible CLI Interface:** Offers command-line arguments to save either the single fastest node or all operational nodes sorted by response time.

### ⚙️ How It Works
1. **URI Decoding:** Decodes standard proxy URI links and Base64 structures.
2. **TCP Ping:** Establishes a raw TCP connection via `socket.create_connection` to calculate connection delay in milliseconds.
3. **Sorting & Output:** Sorts active nodes by response speed and exports the results to specified text files.

### 🚀 Usage

**Prerequisites:**
* Python 3.7+

**Running the Script:**
```bash
# Basic scan (looks for configs.txt by default)
python tester.py

# Specify a custom input file and save the fastest config
python tester.py -f my_configs.txt -o best_config.txt

# Save all working configs sorted by latency with 30 threads
python tester.py -f my_configs.txt -a sorted_working.txt -w 30
