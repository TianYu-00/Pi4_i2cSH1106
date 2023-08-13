# Header

<img src="https://github.com/TianYu-00/RPi4_SomeUsefulStuff/blob/main/SH1106_i2cDisplay_RPi4/i2c_oled_128x64_raspberry_pi_wiring.png"/>
<img src="https://github.com/TianYu-00/RPi4_SomeUsefulStuff/blob/main/SH1106_i2cDisplay_RPi4/SDA_SCL_Diagram.png" />


Below instruction is copied from https://luma-oled.readthedocs.io/en/latest/install.html. Some contents are edited by me to better understand/follow.
notice: This guide is for my own use but is public if anyone else also needs help with assembling and installing it. I am in no way affiliated with Luma or any display manufacturers, im just a end user of their product.  

## Turning on I2C
For Raspberry Pi OS, enable the I2C driver as follows:
```
Run sudo raspi-config
```
 Interfacing Options -> Enable I2C -> Save that and reboot

After rebooting re-check that the `dmesg | grep i2c` command shows whether I2C driver is loaded before proceeding. You can also enable I2C manually if the raspi-config utility is not available.

Optionally, to improve performance, increase the I2C baudrate from the default of 100KHz to 400KHz by altering `/boot/config.txt` to include:

`dtparam=i2c_arm=on,i2c_baudrate=400000`
Then reboot.

Next, add your user to the i2c group and install i2c-tools:
`sudo usermod -a -G i2c pi`
`sudo apt-get install i2c-tools`

Check to see if it works
`i2cdetect -y 1`

Check that the device is communicating properly (if using a rev.1 board, use 0 for the bus, not 1) and determine its address using i2cdetect:
Should be something similar to this:
```
$ i2cdetect -y 1
       0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
  00:          -- -- -- -- -- -- -- -- -- -- -- -- --
  10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
  20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
  30: -- -- -- -- -- -- -- -- -- -- -- -- 3c -- -- --
  40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
  50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
  60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
  70: -- -- -- -- -- -- -- --
```
Enabling The SPI Interface:
`sudo raspi-config`
Interfacing Options - Enable SPI -> Save that and reboot


Ensure that the SPI kernel driver is enabled:
Check to see if it works
`lsmod | grep spi`

Then add your user to the spi and gpio groups:
`sudo usermod -a -G spi,gpio pi`
Log out and back in again to ensure that the group permissions are applied successfully.

## Now that we have all those done were ready to install.
This will normally retrieve all of the dependencies luma.oled requires and install them automatically.
`sudo -H pip3 install --upgrade luma.oled`

### Installing Dependencies
If pip is unable to automatically install its dependencies you will have to add them manually. To resolve the issues you will need to add the appropriate development packages to continue.

If you are using Raspberry Pi OS you should be able to use the following commands to add the required packages:
`sudo apt-get update`
`sudo apt-get install python3 python3-pip python3-pil libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 libtiff5 -y`
`sudo -H pip3 install luma.oled`

luma.oled uses hardware interfaces that require permission to access. After you have successfully installed luma.oled you may want to add the user account that your luma.oled program will run as to the groups that grant access to these interfaces.:

`sudo usermod -a -G spi,gpio,i2c pi`
Replace pi with the name of the account you will be using.


Try this official example script from luma:

```
from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1309, ssd1325, ssd1331, sh1106, sh1107, ws0010

# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
# substitute bitbang_6800(RS=7, E=8, PINS=[25,24,23,27]) below if using that interface
serial = i2c(port=1, address=0x3C)

# substitute ssd1331(...) or sh1106(...) below if using that device
device = sh1106(serial) # change this model to ur display chip model

with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((30, 40), "Hello World", fill="white")

```

Or try out my script that shows the Temp, CPU Usage, Memory Usage, and Pi's public IP:
You could also just download this script straight from my repo in the same directory that this md file is.
in order to use this script you need to first install netifaces.
`pip install luma.oled netifaces`
After that create a python script and try it out urself.
```
import time
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont
import psutil
import netifaces
import socket
# Initialize display
serial = i2c(port=1, address=0x3C)
disp = sh1106(serial)
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        return 'IP not found'
def display_info():
    while True:
        # Get system information
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        temperature = round(float(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1000, 2)
        ip_address = get_ip_address()
        # Create an image
        image = Image.new('1', (disp.width, disp.height))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        # Draw information on the image
        draw.text((0, 48), f'IP: {ip_address}', font=font, fill=255)
        draw.text((0, 0), f'Temp: {temperature} C', font=font, fill=255)
        draw.text((0, 16), f'CPU: {cpu_usage}%', font=font, fill=255)
        draw.text((0, 32), f'Mem: {memory_usage}%', font=font, fill=255)
        
        # Display the image on the OLED screen
        disp.display(image)
        time.sleep(2)  # Update every 2 seconds
if __name__ == '__main__':
    try:
        display_info()
    except KeyboardInterrupt:
        pass
    finally:
        disp.clear()
        disp.display()

```
To automatically run this script you can try and add it to ur crontab
`crontab -e`
if its ur firsttime ever running this command it will show to choose ur editor. Just choose the 1st one.
Now that were in, go all the way down to the bottom of a new line, add this line of code to make it run automatically after reboot.
`@reboot python3 <directoryOfTheScript>`
for example
`@reboot python3 /home/pi/statdisplay.py`
`statdisplay.py` is ur python script file name.

press crtl o (to say you want to write the file). then
press Enter (to say you want to overwrite existing file). then
press ctrl x (to exit nano)

when its saved, do a reboot and check it out.
`sudo reboot`







