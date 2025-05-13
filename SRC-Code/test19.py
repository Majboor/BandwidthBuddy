import rumps

class ProcessMonitorApp(rumps.App):
    def __init__(self):
        super(ProcessMonitorApp, self).__init__("WiFi Monitor", icon=None)
        self.timer = rumps.Timer(self.refresh_menu, 10)  # Auto-refresh every 10 seconds
        self.timer.start()
        self.refresh_menu()  # immediate load

    def refresh_menu(self, _=None):
        dummy_processes = [
            {"process": "Google Chrome", "total": 5024},
            {"process": "Arc Browser", "total": 2345},
            {"process": "Spotify", "total": 1234},
            {"process": "Postman", "total": 980},
            {"process": "Discord", "total": 820}
        ]

        self.menu.clear()
        self.menu.add(rumps.MenuItem("Manual Refresh", callback=self.manual_refresh))
        self.menu.add(None)

        # Top 5 Usage Apps
        self.menu.add("Top 5 Usage Apps")
        for item in dummy_processes[:5]:
            display = f"{item['process']} ({item['total']} KB)"
            sub_menu = rumps.MenuItem(display)
            sub_menu.add(rumps.MenuItem("Kill Process", callback=self.make_kill_callback(item['process'])))
            sub_menu.add(rumps.MenuItem("Set WiFi Limit (Coming Soon)", callback=self.fake_limit))
            self.menu["Top 5 Usage Apps"].add(sub_menu)

        self.menu.add(None)
        self.menu.add(rumps.MenuItem("Quit", callback=rumps.quit_application))

    @rumps.clicked("Manual Refresh")
    def manual_refresh(self, _):
        self.refresh_menu()

    def make_kill_callback(self, process_name):
        def kill_process(_):
            rumps.notification("Killed", f"Killed process: {process_name}", "")
            self.refresh_menu()
        return kill_process

    def fake_limit(self, _):
        rumps.alert("Feature Coming Soon", "Setting WiFi Limits will be available in a future version!")

if __name__ == "__main__":
    ProcessMonitorApp().run()

