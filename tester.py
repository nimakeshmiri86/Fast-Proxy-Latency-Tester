import socket
import time
import base64
import json
import urllib.parse
import concurrent.futures
import argparse
import sys


def parse_config(config: str):
    config = config.strip()
    try:
        if config.startswith("vless://") or config.startswith("trojan://"):
            parsed = urllib.parse.urlparse(config)
            netloc = parsed.netloc
            if '@' in netloc:
                netloc = netloc.split('@')[1]
            if ':' in netloc:
                host, port = netloc.split(':')
                return host, int(port)

        elif config.startswith("vmess://"):
            b64_str = config[8:]
            b64_str += "=" * ((4 - len(b64_str) % 4) % 4)
            decoded = base64.b64decode(b64_str).decode('utf-8')
            data = json.loads(decoded)
            return data['add'], int(data['port'])

        elif ":" in config and not config.startswith("http"):
            parts = config.split(':')
            return parts[0], int(parts[1])
    except Exception:
        pass

    return None, None


def tcp_ping(config: str, timeout: float = 2.0):
    host, port = parse_config(config)
    if not host or not port:
        return config, float('inf')

    start_time = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            latency = (time.time() - start_time) * 1000
            return config, latency
    except (socket.timeout, ConnectionRefusedError, socket.gaierror, OSError):
        return config, float('inf')


def test_configs(configs: list, max_workers: int = 20, timeout: float = 2.0):
    results = []
    print(f"🔄 Testing {len(configs)} configs...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(tcp_ping, cfg, timeout) for cfg in configs]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda x: x[1])
    return results


def load_configs_from_file(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        if not content.startswith(("vless://", "vmess://", "trojan://")) and "\n" not in content:
            try:
                content += "=" * ((4 - len(content) % 4) % 4)
                content = base64.b64decode(content).decode('utf-8')
            except Exception:
                pass

        lines = [line.strip() for line in content.splitlines() if line.strip()]
        return lines
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="⚡ Fast V2Ray/Xray TCP Latency Tester")
    parser.add_argument("-f", "--file", default="configs.txt",
                        help="Path to file containing configs (default: configs.txt)")
    parser.add_argument("-o", "--output", help="Save the single fastest config to a file")
    parser.add_argument("-a", "--all-output", help="Save all working configs sorted by speed to a file")
    parser.add_argument("-t", "--timeout", type=float, default=2.0,
                        help="Socket connection timeout in seconds (default: 2.0)")
    parser.add_argument("-w", "--workers", type=int, default=20, help="Number of concurrent threads (default: 20)")

    args = parser.parse_args()

    configs = load_configs_from_file(args.file)
    if not configs:
        print("❌ No valid configs found in the file.")
        return

    results = test_configs(configs, max_workers=args.workers, timeout=args.timeout)

    valid_results = [r for r in results if r[1] != float('inf')]

    if not valid_results:
        print("\n❌ All configs failed to connect (Timeout or unreachable).")
        return

    print("\n--- 📊 Test Results ---")
    for config, latency in valid_results:
        display_name = config[:50] + "..." if len(config) > 50 else config
        print(f"[{latency:6.1f} ms] | {display_name}")

    fastest_config, best_latency = valid_results[0]
    print("\n🏆 Fastest Config Found:")
    print(f"⚡ Latency: {best_latency:.1f} ms")
    print(f"🔗 Config:  {fastest_config}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as out:
            out.write(fastest_config + "\n")
        print(f"\n💾 Saved fastest config to '{args.output}'")

    if args.all_output:
        with open(args.all_output, "w", encoding="utf-8") as out:
            for cfg, _ in valid_results:
                out.write(cfg + "\n")
        print(f"💾 Saved all {len(valid_results)} working configs to '{args.all_output}'")


if __name__ == "__main__":
    main()