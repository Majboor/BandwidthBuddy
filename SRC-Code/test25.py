import rumps
import subprocess
import os
from operator import itemgetter

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

ALERT_MB_THRESHOLD = 200  # 200MB per refresh

class ProcessMonitorApp(rumps.App):
    def __init__(self):
        super(ProcessMonitorApp, self).__init__("WiFi Monitor", icon=None, menu=["Loading..."])
        self.previous_data = {}
        self.timer = rumps.Timer(self.refresh_menu, 10)
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
                output, _ = proc.communicate(timeout=3)
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
        self.menu.add(rumps.MenuItem("Restart (Close All Windows + Kill Apps)", callback=self.restart_all_apps))
        self.menu.add(None)

        live_usage = []

        for item in processes:
            current_total = item['total']
            process_name = item['process']
            prev_total = self.previous_data.get(process_name, current_total)
            delta = max(current_total - prev_total, 0)
            usage_in_mb = round(delta / 1048576, 2)

            # Save current total for next round
            self.previous_data[process_name] = current_total

            item['delta'] = usage_in_mb
            live_usage.append(item)

        # Sort by live usage
        live_usage.sort(key=lambda x: x['delta'], reverse=True)

        # Usage Alerts
        for item in live_usage:
            if item['delta'] > ALERT_MB_THRESHOLD:
                rumps.notification("High Usage Alert", f"{item['process']} used {item['delta']} MB", "")

        # Top 5 Usage Apps
        self.menu.add("Top 5 Usage Apps")
        for item in live_usage[:5]:
            display = f"{item['process']} ({item['delta']} MB)"
            sub_menu = rumps.MenuItem(display)
            sub_menu.add(rumps.MenuItem("Kill Process", callback=self.make_kill_callback(item['process'])))
            sub_menu.add(rumps.MenuItem("Super Kill Process", callback=self.make_superkill_callback(item['process'])))
            sub_menu.add(rumps.MenuItem("Set WiFi Limit (Coming Soon)", callback=self.fake_limit))
            self.menu["Top 5 Usage Apps"].add(sub_menu)

        self.menu.add(None)

        # Grouped Processes
        grouped = {"Browser": [], "Programming & IDE": [], "Extras": [], "System": [], "Unknown": []}
        for data in live_usage:
            grouped[data['group']].append(data)

        for group_name, items in grouped.items():
            if items:
                group_menu = rumps.MenuItem(group_name)
                for item in items:
                    display = f"{item['process']} ({item['delta']} MB)"
                    process_menu = rumps.MenuItem(display)
                    process_menu.add(rumps.MenuItem("Kill Process", callback=self.make_kill_callback(item['process'])))
                    process_menu.add(rumps.MenuItem("Super Kill Process", callback=self.make_superkill_callback(item['process'])))
                    process_menu.add(rumps.MenuItem("Set WiFi Limit (Coming Soon)", callback=self.fake_limit))
                    group_menu.add(process_menu)
                self.menu.add(group_menu)

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
        confirm = rumps.alert(
            "Are you sure?",
            "This will close all Finder windows, kill Finder, Dock, SystemUIServer, browsers, and apps.",
            ok="Yes", cancel="No"
        )
        if confirm == 1:
            os.system("osascript -e 'tell application \"Finder\" to close every window'")
            os.system("killall Finder Dock SystemUIServer")
            os.system("killall -9 'Google Chrome' 'Spotify' 'WhatsApp' 'Postman' 'Discord' 'Electron' 'Arc' 'zoom.us'")

if __name__ == "__main__":
    ProcessMonitorApp().run()

