from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont
import psutil
import datetime
import requests
import netifaces
import time

# Set up the I2C interface
serial = i2c(port=1, address=0x3C)

# Create an SH1106 OLED display
device = sh1106(serial, rotate=0)  # You might need to adjust the 'rotate' parameter

# Load The font
font = ImageFont.load_default()

while True:
    # Clear the display
    image = Image.new("1", (device.width, device.height))
    draw = ImageDraw.Draw(image)

    # Get CPU temperature using psutil
    cpu_temperature = psutil.sensors_temperatures().get("cpu_thermal", [])
    if cpu_temperature:
        cpu_temp = f"CPU Temp    : {cpu_temperature[0].current:.1f}°C"
        draw.text((0, 0), cpu_temp, font=font, fill="white")

    # Get CPU usage using psutil
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_usage_text = f"CPU Used    : {cpu_usage:.1f}%"
    draw.text((0, 10), cpu_usage_text, font=font, fill="white")

    # Get memory usage using psutil
    memory = psutil.virtual_memory()
    memory_usage_text = f"Memory Used : {memory.percent:.1f}%"
    draw.text((0, 20), memory_usage_text, font=font, fill="white")

    # Get storage usage
    disk_usage = psutil.disk_usage("/")
    storage_used_gb = disk_usage.used / (1024 ** 3)  # Convert bytes to gigabytes
    storage_text = f"Storage Used: {storage_used_gb:.2f}gb"
    draw.text((0, 30), storage_text, font=font, fill="white")

    # Get public IP address
    try:
        public_ip = requests.get("https://api.ipify.org?format=json").json()["ip"]
        draw.text((0, 40), f"IP  : {public_ip}", font=font, fill="white")
    except Exception as e:
        draw.text((0, 40), "IP  : N/A", font=font, fill="white")

    # Get local IPv4 address
    try:
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            if interface != "lo":
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    local_ip = addrs[netifaces.AF_INET][0]['addr']
                    draw.text((0, 50), f"IPv4: {local_ip}", font=font, fill="white")
                    break
    except Exception as e:
        draw.text((0, 50), "IPv4: N/A", font=font, fill="white")

    # # Get current date and time
    # current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # draw.text((0, 40), current_datetime, font=font, fill="white")

    # Show the image on the display
    device.display(image)

    # Wait for x seconds before refreshing. 
    # If you want live update just change this to 1sec to make it constantly update every 1 second.
    time.sleep(5)

