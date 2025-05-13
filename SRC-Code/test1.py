import subprocess
import time

def get_network_usage(interval=1):
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

                        if bytes_in > 0 or bytes_out > 0:
                            print(f"Process: {process_name:30} | Download: {bytes_in:10} Bytes | Upload: {bytes_out:10} Bytes")
            else:
                print("No active traffic detected.")

        except subprocess.TimeoutExpired:
            print("Timeout expired while running nettop.")

        time.sleep(interval)

if __name__ == "__main__":
    get_network_usage()

