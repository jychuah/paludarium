#!/usr/bin/python

from gi.repository import Gtk, GLib, GObject
from requests import ConnectionError
import threading
import time
from gi.repository import GObject
from data import Data
from threading import Thread
from time import sleep

win = None
updateNum = 1
data = Data()
data.begin()

class PaludariumWindow(Gtk.Window):
    updateNum = 0
    def __init__(self):
        Gtk.Window.__init__(self, title="Paludarium")
        self.connect("delete-event", Gtk.main_quit)
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.add(self.box)
        self.humidity = Gtk.Label("Humidity")
        self.box.pack_start(self.humidity, True, True, 0)
        self.temperature = Gtk.Label("temperature")
        self.box.pack_start(self.temperature, True, True, 0)
        self.current_program = Gtk.Label("current_program")
        self.box.pack_start(self.current_program, True, True, 0)
        self.lights_control = Gtk.Label("lights control")
        self.box.pack_start(self.lights_control, True, True, 0)
        self.lights_0 = Gtk.Label("lights 0")
        self.box.pack_start(self.lights_0, True, True, 0)
        self.lights_1 = Gtk.Label("lights 1")
        self.box.pack_start(self.lights_1, True, True, 0)
        self.lights_2 = Gtk.Label("lights 2")
        self.box.pack_start(self.lights_2, True, True, 0)
        self.lights_3 = Gtk.Label("lights 3")
        self.box.pack_start(self.lights_3, True, True, 0)
        self.relays_control = Gtk.Label("relays control")
        self.box.pack_start(self.relays_control, True, True, 0)
        self.relays_0 = Gtk.Label("relay 0")
        self.box.pack_start(self.relays_0, True, True, 0)
        self.relays_1 = Gtk.Label("relay 1")
        self.box.pack_start(self.relays_1, True, True, 0)

    def map_status(self):
        self.set_title(data.state["name"])
        self.current_program.set_text("Current program: " + data.state["state"]["current_program"])
        self.temperature.set_text("Temperature: " + str(data.state["state"]["temperature"]))
        self.humidity.set_text("Humidity: " + str(data.state["state"]["humidity"]))
        self.lights_control.set_text("Lights: " + str(data.state["state"]["lights"]["control"]))
        self.lights_0.set_text(data.state["state"]["lights"]["names"][0] + ": " + str(data.state["state"]["lights"]["values"][0]))
        self.lights_1.set_text(data.state["state"]["lights"]["names"][1] + ": " + str(data.state["state"]["lights"]["values"][1]))
        self.lights_2.set_text(data.state["state"]["lights"]["names"][2] + ": " +  str(data.state["state"]["lights"]["values"][2]))
        self.lights_3.set_text(data.state["state"]["lights"]["names"][3] + ": " +  str(data.state["state"]["lights"]["values"][3]))
        self.relays_control.set_text("Relays: " + str(data.state["state"]["relays"]["control"]))
        self.relays_0.set_text(data.state["state"]["relays"]["names"][0] + ": " +  str(data.state["state"]["relays"]["values"][0]))
        self.relays_1.set_text(data.state["state"]["relays"]["names"][1] + ": " +  str(data.state["state"]["relays"]["values"][1]))

    def update(self):
        GObject.timeout_add(1, self.map_status())

def timeout():
    global data
    if data.connected:
        try:
            data.ref.child("state/temperature").set(int(data.state["state"]["temperature"]) + 1)
        except ConnectionError:
            data.log.info("Could not write to Firebase")

    GObject.timeout_add(2000, timeout)


def app_main():
    global win
    win = PaludariumWindow()

    def example_target():
        data.connect_sse_state(win)

    win.show_all()
    GObject.timeout_add(2000, timeout)

    thread = threading.Thread(target=example_target)
    thread.daemon = True
    thread.start()




if __name__ == "__main__":
    # Calling GObject.threads_init() is not needed for PyGObject 3.10.2+
    GObject.threads_init()

    app_main()
    Gtk.main()