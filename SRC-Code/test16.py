import rumps

class MyApp(rumps.App):
    @rumps.clicked("Hello")
    def hello(self, _):
        rumps.alert("Hi!")

if __name__ == "__main__":
    MyApp("Test App").run()

