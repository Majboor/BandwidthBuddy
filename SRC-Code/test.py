import subprocess
import time

def get_network_usage(interval=1):
    print(f"Monitoring network usage per process every {interval} second(s)...\n")
    while True:
        # Run nettop command silently and get output
        result = subprocess.run(
            ["nettop", "-P", "-L", "1", "-x"],
            capture_output=True,
            text=True
        )
        lines = result.stdout.splitlines()

        for line in lines:
            if "tcp" in line or "udp" in line:
                parts = line.split(',')
                if len(parts) > 9:
                    process_name = parts[0]
                    interface = parts[1]
                    rx_bytes = parts[7]  # Received bytes
                    tx_bytes = parts[8]  # Transmitted bytes
                    print(f"App: {process_name} | RX: {rx_bytes} bytes | TX: {tx_bytes} bytes")

        time.sleep(interval)

if __name__ == "__main__":
    get_network_usage()

