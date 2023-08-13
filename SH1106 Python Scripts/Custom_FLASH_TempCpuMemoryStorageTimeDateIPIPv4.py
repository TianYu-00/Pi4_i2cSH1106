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

info_list = [
    ("CPU:", "Memory:", "Storage:"),
    ("IP:", "IPv4:", "DateTime:", "Switches:")
]

info_index = 0

info_update_interval = 1  # Update info every 1 second
switch_interval = 5       # Switch between info sets in x interval
switch_counter = 0

while True:
    # Clear the display
    image = Image.new("1", (device.width, device.height))
    draw = ImageDraw.Draw(image)

    y_position = 0
    # Display "Temp" information at the top
    cpu_temperature = psutil.sensors_temperatures().get("cpu_thermal", [])
    if cpu_temperature:
        temp_text = f"Temp: {cpu_temperature[0].current:.1f}°C"
        draw.text((0, y_position), temp_text, font=font, fill="white")
        y_position += 15

    info_set = info_list[info_index]

    for info in info_set:
        if info == "Switches:":
            break

        if info == "DateTime:":
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            draw.text((0, y_position), current_datetime, font=font, fill="white")
        else:
            if info == "CPU:":
                cpu_usage = psutil.cpu_percent(interval=1)
                info_text = f"{info} {cpu_usage:.1f}%"
            elif info == "Memory:":
                memory = psutil.virtual_memory()
                info_text = f"{info} {memory.percent:.1f}%"
            elif info == "Storage:":
                disk_usage = psutil.disk_usage("/")
                storage_used_gb = disk_usage.used / (1024 ** 3)  # Convert bytes to gigabytes
                info_text = f"{info} {storage_used_gb:.2f}gb"
            elif info == "IP:":
                try:
                    public_ip = requests.get("https://api.ipify.org?format=json").json()["ip"]
                    info_text = f"{info} {public_ip}"
                except Exception as e:
                    info_text = f"{info} N/A"
            elif info == "IPv4:":
                try:
                    interfaces = netifaces.interfaces()
                    for interface in interfaces:
                        if interface != "lo":
                            addrs = netifaces.ifaddresses(interface)
                            if netifaces.AF_INET in addrs:
                                local_ip = addrs[netifaces.AF_INET][0]['addr']
                                info_text = f"{info} {local_ip}"
                                break
                except Exception as e:
                    info_text = f"{info} N/A"

            draw.text((0, y_position), info_text, font=font, fill="white")

        y_position += 15

    # Show the image on the display
    device.display(image)

    # Update the info every 1 second
    time.sleep(info_update_interval)

    # Check if it's time to switch between info sets
    switch_counter += info_update_interval
    if switch_counter >= switch_interval:
        switch_counter = 0
        info_index = (info_index + 1) % len(info_list)

