#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# stdlib
import array, threading, random, time

# GTK+3 through gobject-introspection
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Gdk

# PyUSB
import usb.core
import usb.util


class USBReader(threading.Thread):
	def __init__(self):
		#super().__init__()
		threading.Thread.__init__(self)
		self.daemon = True
		
		self.value = 0.0
	
	def run(self):
		VENDOR_ID = 0x0922
		PRODUCT_ID = 0x8005
		
		DATA_MODE_GRAMS = 2
		DATA_MODE_OUNCES = 11
		
		# find the USB device
		try:
			device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
		except usb.core.NoBackendError:
			device = None
			print("no usb backend")
		if device:
			print("found device")
			#print(device)
			
			# use the first/default configuration
			try:
				device.set_configuration()
			except usb.core.USBError as err:
				if err.errno == 16:
					print("device busy, trying to detach it")
					device.detach_kernel_driver(0)
					device.set_configuration()
				else:
					raise
			
			# first endpoint
			endpoint = device[0][(0,0)][0]
			
			while True:
				# read a data packet
				attempts = 10
				data = None
				while data is None and attempts > 0:
					#print("trying to read data..")
					try:
						data = device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
					except usb.core.USBError as e:
						data = None
						if e.args == ('Operation timed out',):
							attempts -= 1
							continue
				
				if data is None:
					print("could not read data!")
					self.value = 0
					break
				
				else:
					#print("raw data:", data)
					if data[2] == DATA_MODE_GRAMS:
						grams = data[4] + data[5] * 256
						self.value = grams
					else:
						#print("metric mode not detected")
						self.value = 0
		
		else:
			print("could not find device, using TEST DATA")
			while True:
				self.value = random.normalvariate(625, 200)
				time.sleep(0.25)


class ScaleApp():
	def __init__(self):
		self.ur = USBReader()
		self.ur.start()
		
		self.build_UI()
		
		GObject.timeout_add(10, self.get_value)
	
	def build_UI(self):
		self.UIB = Gtk.Builder()
		self.UIB.add_from_file("scale.glade")
		self.UIB.connect_signals(self)
		
		self.UIB.get_object("weight").set_alignment(xalign=1.0)
		self.UIB.get_object("info").set_alignment(xalign=0.5)
		
		screen = Gdk.Screen.get_default()
		css_provider = Gtk.CssProvider()
		css_provider.load_from_path('scale.css')
		context = Gtk.StyleContext()
		context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
		
		self.win = self.UIB.get_object("main_window")
		self.win.set_default_size(450, 150)
		self.win.set_position(Gtk.WindowPosition.CENTER)
		self.win.show_all()
	
	def get_value(self):
		g = self.ur.value
		self.UIB.get_object("weight").set_text("%i" % g)
		info = self.UIB.get_object("info")
		if g <= 0: info.set_text("---")
		elif g < 250: info.set_text("< 250")
		elif g < 500: info.set_text("< 500")
		elif g < 1000: info.set_text("< 1000")
		elif g < 2000: info.set_text("< 2000")
		else: info.set_text("OVER MAX")
		return True
	
	def copy_to_clipboard(self, widget):
		cb = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		cb.set_text(self.UIB.get_object("weight").get_text(), -1)
	
	def quit(self, widget):
		Gtk.main_quit()
	
	def on_key_press(self, widget, ev):
		if ev.keyval == Gdk.KEY_Escape:
			self.win.destroy()
		elif ev.keyval == 99:
			self.copy_to_clipboard(None)
	
	def on_delete_window(self, *args):
		Gtk.main_quit(*args)


if __name__ == "__main__":
	app = ScaleApp()
	Gtk.main()

