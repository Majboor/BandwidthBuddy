import subprocess
import time
import os
from operator import itemgetter

# Define groups
BROWSERS = ["Google Chrome", "Google Chrome H", "com.apple.WebKi", "Arc", "zen"]
PROGRAMMING_IDE = ["Trae", "Postman", "GitHub Desktop"]
EXTRAS = ["Spotify", "Discord", "WhatsApp", "Electron", "ChatGPT", "ChatGPTHelper"]
SYSTEM = ["mDNSResponder", "apsd", "WeatherWidget", "manager", "identityservice", "netbiosd", "cloudflared"]

GROUPS = {
    "Browser": BROWSERS,
    "Programming & IDE": PROGRAMMING_IDE,
    "Extras": EXTRAS,
    "System": SYSTEM
}

def classify_process(name):
    for browser in BROWSERS:
        if browser.lower() in name.lower():
            return "Browser"
    for prog in PROGRAMMING_IDE:
        if prog.lower() in name.lower():
            return "Programming & IDE"
    for extra in EXTRAS:
        if extra.lower() in name.lower():
            return "Extras"
    for sys in SYSTEM:
        if sys.lower() in name.lower():
            return "System"
    return "Unknown"

def get_network_usage(interval=10):
    print(f"Monitoring network usage every {interval} second(s)...\n")
    while True:
        try:
            # Run nettop command
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
                            group = classify_process(process_name)
                            usage_data.append({
                                "process": process_name,
                                "download": bytes_in,
                                "upload": bytes_out,
                                "total": total_bytes,
                                "group": group
                            })

                # Sort by total bytes
                usage_data.sort(key=itemgetter('total'), reverse=True)

                # Clear screen
                print("\033c", end="")

                # Grouped display
                groups = {"Browser": [], "Programming & IDE": [], "Extras": [], "System": [], "Unknown": []}
                for data in usage_data:
                    groups[data['group']].append(data)

                for group_name, group_data in groups.items():
                    if group_data:
                        print(f"\n=== {group_name} ===")
                        print(f"{'Process Name':<30} {'Download (KB)':>15} {'Upload (KB)':>15} {'Total (KB)':>15}")
                        print("-" * 80)
                        for data in group_data:
                            print(f"{data['process']:<30} {data['download']//1024:>15} {data['upload']//1024:>15} {data['total']//1024:>15}")

            else:
                print("No active traffic detected.")

        except subprocess.TimeoutExpired:
            print("Timeout expired while running nettop.")

        # Control options
        print("\nOptions:")
        print("Press 'k' + Enter → Select a category to kill")
        print("Press Enter to continue monitoring...")

        user_input = input().strip().lower()
        if user_input == 'k':
            select_category_to_kill()

        time.sleep(interval)

def select_category_to_kill():
    print("\nSelect which group you want to kill:")
    print("1 → Browser")
    print("2 → Programming & IDE")
    print("3 → Extras")
    print("4 → System")
    print("5 → Cancel (Do nothing)")
    
    choice = input("Enter your choice (1/2/3/4/5): ").strip()

    if choice == '1':
        kill_group("Browser")
    elif choice == '2':
        kill_group("Programming & IDE")
    elif choice == '3':
        kill_group("Extras")
    elif choice == '4':
        kill_group("System")
    else:
        print("Cancelled. No action taken.")

def kill_group(group_name):
    print(f"Killing all processes in {group_name} group...")
    apps = GROUPS.get(group_name, [])
    for app_name in apps:
        try:
            os.system(f"pkill -f '{app_name}'")
            print(f"Killed {app_name}")
        except Exception as e:
            print(f"Error killing {app_name}: {e}")

if __name__ == "__main__":
    get_network_usage()

