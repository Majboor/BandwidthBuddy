import rumps
import subprocess
import os
from operator import itemgetter

# Define process groups
BROWSERS = ["Google Chrome", "Google Chrome H", "com.apple.WebKi", "Arc", "zen"]
PROGRAMMING_IDE = ["Trae", "Postman", "GitHub Desktop", "Pieces OS", "postgres"]
EXTRAS = ["Spotify", "Discord", "WhatsApp", "Electron", "ChatGPT", "ChatGPTHelper", "zoom.us"]
SYSTEM = ["mDNSResponder", "apsd", "WeatherWidget", "manager", "identityservice", "netbiosd", "cloudflared", "rapportd", "com.apple.geod"]

GROUPS = {
    "Browser": BROWSERS,
    "Programming & IDE": PROGRAMMING_IDE,
    "Extras": EXTRAS,
    "System": SYSTEM
}

class ProcessMonitorApp(rumps.App):
    def __init__(self):
        super(ProcessMonitorApp, self).__init__("📶 WiFi Monitor", icon=None, menu=["Refresh", None])
        self.refresh_menu()

    @rumps.clicked("Refresh")
    def refresh(self, _):
        self.refresh_menu()

    def classify_process(self, name):
        for group_name, apps in GROUPS.items():
            for app in apps:
                if app.lower() in name.lower():
                    return group_name
        return "Unknown"

    def fetch_network_processes(self):
        try:
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
                            group = self.classify_process(process_name)
                            usage_data.append({
                                "process": process_name,
                                "download": bytes_in,
                                "upload": bytes_out,
                                "total": total_bytes,
                                "group": group
                            })

                usage_data.sort(key=itemgetter('total'), reverse=True)
            return usage_data

        except subprocess.TimeoutExpired:
            rumps.alert("Timeout", "Failed to fetch processes in time.")
            return []

    def refresh_menu(self):
        processes = self.fetch_network_processes()
        
        self.menu.clear()
        self.menu.add(rumps.MenuItem("Refresh", callback=self.refresh))
        self.menu.add(None)  # Separator

        grouped = {"Browser": [], "Programming & IDE": [], "Extras": [], "System": [], "Unknown": []}
        for data in processes:
            grouped[data['group']].append(data)

        for group_name, items in grouped.items():
            if items:
                group_menu = rumps.MenuItem(group_name)
                for item in items:
                    process_display = f"{item['process']} ({item['total']//1024} KB)"
                    group_menu.add(rumps.MenuItem(process_display, callback=self.make_kill_callback(item['process'])))
                self.menu.add(group_menu)

        self.menu.add(None)  # Separator
        self.menu.add("Quit", callback=rumps.quit_application)

    def make_kill_callback(self, process_name):
        def kill_process(_):
            os.system(f"pkill -f '{process_name}'")
            rumps.notification("Killed", f"Killed process: {process_name}", "")
            self.refresh_menu()
        return kill_process

if __name__ == "__main__":
    ProcessMonitorApp().run()

