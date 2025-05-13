import subprocess
import time
from operator import itemgetter

def get_network_usage(interval=10):
    print(f"Monitoring network usage per process every {interval} second(s)...\n")
    while True:
        try:
            # Run nettop command and capture output
            result = subprocess.run(
                ["nettop", "-P", "-L", "1", "-x"],
                capture_output=True,
                text=True,
                timeout=5
            )

            output = result.stdout.strip()
            usage_data = []

            if output:
                lines = output.splitlines()

                # Ignore the first header line
                for line in lines[1:]:
                    parts = line.split(',')
                    if len(parts) >= 6:
                        process_name = parts[1]
                        bytes_in = parts[4] or "0"
                        bytes_out = parts[5] or "0"

                        try:
                            bytes_in = int(bytes_in)
                            bytes_out = int(bytes_out)
                        except ValueError:
                            continue

                        total_bytes = bytes_in + bytes_out

                        if total_bytes > 0:
                            usage_data.append({
                                "process": process_name,
                                "download": bytes_in,
                                "upload": bytes_out,
                                "total": total_bytes
                            })

                # Sort data by total bytes (download + upload) descending
                usage_data.sort(key=itemgetter('total'), reverse=True)

                # Clear screen for clean view
                print("\033c", end="")

                print(f"{'Process Name':<30} {'Download (KB)':>15} {'Upload (KB)':>15} {'Total (KB)':>15}")
                print("-" * 80)

                for data in usage_data:
                    print(f"{data['process']:<30} {data['download']//1024:>15} {data['upload']//1024:>15} {data['total']//1024:>15}")
            else:
                print("No active traffic detected.")

        except subprocess.TimeoutExpired:
            print("Timeout expired while running nettop.")

        time.sleep(interval)

if __name__ == "__main__":
    get_network_usage()

