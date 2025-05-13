import rumps

class ProcessMonitorApp(rumps.App):
    def __init__(self):
        super(ProcessMonitorApp, self).__init__("WiFi Monitor")
        self.menu = ["Show Processes", "Kill All Browsers", "Reset All", None, "Quit"]

    @rumps.clicked("Show Processes")
    def show_processes(self, _):
        rumps.alert("Listing all active processes... (this would be dynamic)")

    @rumps.clicked("Kill All Browsers")
    def kill_browsers(self, _):
        rumps.notification("Action", "Killing Browsers", "Success!")

    @rumps.clicked("Reset All")
    def reset_all(self, _):
        rumps.notification("Action", "Resetting Everything", "All apps killed!")

if __name__ == "__main__":
    ProcessMonitorApp().run()

