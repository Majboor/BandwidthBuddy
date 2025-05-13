import rumps
import subprocess
import os
from operator import itemgetter

# Define groups
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
        super(ProcessMonitorApp, self).__init__("WiFi Monitor", icon=None, menu=["Loading..."])
        self.timer = rumps.Timer(self.refresh_menu, 10)  # Auto-refresh every 10 seconds
        self.timer.start()
        self.refresh_menu()

    def classify_process(self, name):
        for group_name, apps in GROUPS.items():
            for app in apps:
                if app.lower() in name.lower():
                    return group_name
        return "Unknown"

    def fetch_network_processes(self):
        try:
            proc = subprocess.Popen(
                ["nettop", "-P", "-L", "1", "-x"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            try:
                output, _ = proc.communicate(timeout=3)  # 3 second timeout
            except subprocess.TimeoutExpired:
                proc.kill()
                output, _ = proc.communicate()

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

        except Exception as e:
            print(f"Error fetching processes: {e}")
            return []

    def refresh_menu(self, _=None):
        processes = self.fetch_network_processes()

        self.menu.clear()
        self.menu.add(rumps.MenuItem("Manual Refresh", callback=self.manual_refresh))
        self.menu.add(rumps.MenuItem("Restart (Kill All Apps)", callback=self.restart_all_apps))
        self.menu.add(None)

        if processes:
            # Usage Alerts
            for item in processes:
                if item['total'] // 1024 > 50:
                    rumps.notification("High Usage Alert", f"{item['process']} has used {item['total']//1024} MB", "")

            # Top 5 Usage Apps
            self.menu.add("Top 5 Usage Apps")
            for item in processes[:5]:
                display = f"{item['process']} ({item['total']//1024} KB)"
                sub_menu = rumps.MenuItem(display)
                sub_menu.add(rumps.MenuItem("Kill Process", callback=self.make_kill_callback(item['process'])))
                sub_menu.add(rumps.MenuItem("Super Kill Process", callback=self.make_superkill_callback(item['process'])))
                sub_menu.add(rumps.MenuItem("Set WiFi Limit (Coming Soon)", callback=self.fake_limit))
                self.menu["Top 5 Usage Apps"].add(sub_menu)

            self.menu.add(None)

            # Grouped by category
            grouped = {"Browser": [], "Programming & IDE": [], "Extras": [], "System": [], "Unknown": []}
            for data in processes:
                grouped[data['group']].append(data)

            for group_name, items in grouped.items():
                if items:
                    group_menu = rumps.MenuItem(group_name)
                    for item in items:
                        process_display = f"{item['process']} ({item['total']//1024} KB)"
                        process_menu = rumps.MenuItem(process_display)
                        process_menu.add(rumps.MenuItem("Kill Process", callback=self.make_kill_callback(item['process'])))
                        process_menu.add(rumps.MenuItem("Super Kill Process", callback=self.make_superkill_callback(item['process'])))
                        process_menu.add(rumps.MenuItem("Set WiFi Limit (Coming Soon)", callback=self.fake_limit))
                        group_menu.add(process_menu)
                    self.menu.add(group_menu)
        else:
            self.menu.add("No active network processes found.")

        self.menu.add(None)
        self.menu.add(rumps.MenuItem("Quit", callback=rumps.quit_application))

    @rumps.clicked("Manual Refresh")
    def manual_refresh(self, _):
        self.refresh_menu()

    def make_kill_callback(self, process_name):
        def kill_process(_):
            os.system(f"pkill -f '{process_name}'")
            rumps.notification("Killed", f"Killed process: {process_name}", "")
            self.refresh_menu()
        return kill_process

    def make_superkill_callback(self, process_name):
        def super_kill_process(_):
            rumps.alert("Super Kill Attempt", "Trying to kill forcefully with sudo...")
            os.system(f"sudo pkill -9 -f '{process_name}'")
            rumps.notification("Super Killed", f"Force killed process: {process_name}", "")
            self.refresh_menu()
        return super_kill_process

    def fake_limit(self, _):
        rumps.alert("Feature Coming Soon", "Setting WiFi Limits will be available in a future version!")

    def restart_all_apps(self, _):
        confirm = rumps.alert("Are you sure?", "This will kill all major apps including Finder, Dock, SystemUIServer and restart them.", ok="Yes", cancel="No")
        if confirm == 1:
            os.system("killall Finder Dock SystemUIServer")
            os.system("killall -9 'Google Chrome' 'Spotify' 'WhatsApp' 'Postman' 'Discord' 'Electron' 'Arc' 'zoom.us'")

if __name__ == "__main__":
    ProcessMonitorApp().run()

