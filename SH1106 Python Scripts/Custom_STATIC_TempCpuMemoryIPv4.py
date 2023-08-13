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