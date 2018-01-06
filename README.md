# scale-reader
Simple display of weight from a DYMO USB scale.

![scale-reader screenshot](https://www.xixenter.com/stuff/scale-reader-screenshot.png)

## Linux
! usb.core.USBError: [Errno 13] Access denied (insufficient permissions)

$ echo /etc/udev/rules.d/99-scale-reader.rules
SUBSYSTEM=="usb", ATTR{idVendor}=="0922", ATTR{idProduct}=="8005", GROUP="dialout", MODE="0666"
$ sudo udevadm control --reload-rules

## Windows
- python3
- pygi aio bundle
- pip install pyusb
- libusb-win32
- Using the libusb-win32 Filter Wizard, install a device filter for the scale. It will show up in the list as “vid:0922 pid:8005 rev:0100 USB Input Device”.
