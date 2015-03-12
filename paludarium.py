#!/usr/bin/python

from gi.repository import Gtk
import threading
import time
from gi.repository import GObject

win = None
updateNum = 1

class PaludariumWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="Monsoon Birder")
		self.button = Gtk.Button(label="Click Here")
		self.button.connect("clicked", self.on_button_clicked)
		self.add(self.button)

	def on_button_clicked(self, widget):
		print("Hello World")



def timeout():
	global updateNum
	global win
	updateNum = updateNum + 1
	win.button.set_label(str(updateNum))
	GObject.timeout_add(2000, timeout)

			

win = PaludariumWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
GObject.timeout_add(2000, timeout)
Gtk.main()
