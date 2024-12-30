import pygame
import serial
import struct
import threading
import time
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 320, 240  # Raspberry Pi display resolution
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Sensor Data Visualization')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Convert Pygame colors to Matplotlib colors
def pygame_color_to_matplotlib(pygame_color):
    return [c / 255.0 for c in pygame_color]

# Global variables to store sensor data
sensor_data = {
    'humidity': 0.0,
    'temperature': 0.0,
    'ph': 0.0,
    'n': 0.0,
    'p': 0.0,
    'k': 0.0
}

# Function to calculate CRC16
def calculate_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, byteorder='little')

# Function to read data from the sensor
def read_sensor_data(port):
    # Construct Modbus RTU request
    slave_address = 0x01
    function_code = 0x03
    starting_address = 0x0000
    num_registers = 0x0007
    crc = calculate_crc(bytes([slave_address, function_code, starting_address >> 8, starting_address & 0xFF, 
                                num_registers >> 8, num_registers & 0xFF]))

    request = bytes([slave_address, function_code, starting_address >> 8, starting_address & 0xFF, 
                     num_registers >> 8, num_registers & 0xFF]) + crc

    # Send request and read response
    with serial.Serial(port, baudrate=4800, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, 
                       stopbits=serial.STOPBITS_ONE, timeout=0.1) as ser:
        ser.write(request)
        response = ser.read(7 * 2 + 5)  # 7 registers * 2 bytes per register + 5 bytes for address, function code, byte count, CRC

    # Parse response
    data = response[3:-2]  # Exclude address, function code, byte count, and CRC
    values = struct.unpack(f'>{len(data)//2}H', data)  # Assuming unsigned short (2 bytes per register)
    
    # Convert data to meaningful values
    humidity = values[0] / 10.0
    temperature = values[1] / 10.0
    ph = values[3] / 10.0
    n = values[4] / 10.0
    p = values[5] / 10.0
    k = values[6] / 10.0

    return humidity, temperature, ph, n, p, k

# Function to continuously read data from the sensor
def continuous_read(port):
    global sensor_data
    while True:
        try:
            humidity, temperature, ph, n, p, k = read_sensor_data(port)
            sensor_data['humidity'] = humidity
            sensor_data['temperature'] = temperature
            sensor_data['ph'] = ph
            sensor_data['n'] = n
            sensor_data['p'] = p
            sensor_data['k'] = k
            
            # Save to log file
            log_file_path = r'D:\skripsi\NPK\sensor_log.log'
            log_data = f"{time.strftime('%Y-%m-%d %H:%M:%S')}, {temperature:.1f}, {humidity:.1f}, {ph:.1f}, {n:.1f}, {p:.1f}, {k:.1f}\n"
            with open(log_file_path, 'a') as log_file:
                log_file.write(log_data)
                
        except Exception as e:
            print(f"Error reading from port {port}: {e}")
        time.sleep(2)  # Wait for 2 seconds before the next read

# Start the sensor reading in a separate thread
port_name = 'COM3'  # Change this to your port name
threading.Thread(target=continuous_read, args=(port_name,)).start()

# Function to draw a half donut chart
def draw_half_donut_chart(value, max_value, color, position, parameter_name):
    fig, ax = plt.subplots(figsize=(1.0, 1.0))  # Smaller size
    size = 0.4
    vals = [value, max_value - value]
    ax.pie(vals, radius=1, colors=[pygame_color_to_matplotlib(color), "white"], startangle=90, counterclock=False, wedgeprops=dict(width=size, edgecolor='w'))
    ax.text(0, 0, f'{value:.1f}', horizontalalignment='center', verticalalignment='center', fontsize=8, color=pygame_color_to_matplotlib(BLACK))
    ax.text(0, -0.5, parameter_name, horizontalalignment='center', verticalalignment='center', fontsize=8, color=pygame_color_to_matplotlib(BLACK))
    canvas = FigureCanvas(fig)
    canvas.draw()
    raw_data = canvas.buffer_rgba().tobytes()
    size = canvas.get_width_height()

    chart_surface = pygame.image.fromstring(raw_data, size, "RGBA")
    screen.blit(chart_surface, position)
    plt.close(fig)

# Function to draw a line chart
def draw_line_chart(data, color, position, min_value=0, max_value=20, max_length=10):
    if len(data) > max_length:
        data.pop(0)
    fig, ax = plt.subplots(figsize=(1.5, 0.8))  # Smaller size
    ax.plot(data, color=pygame_color_to_matplotlib(color))
    ax.set_ylim(min_value, max_value)
    ax.tick_params(axis='both', which='major', labelsize=6)  # Reduce tick label size
    canvas = FigureCanvas(fig)
    canvas.draw()
    raw_data = canvas.buffer_rgba().tobytes()
    size = canvas.get_width_height()

    chart_surface = pygame.image.fromstring(raw_data, size, "RGBA")
    screen.blit(chart_surface, position)
    plt.close(fig)

# Initialize data storage for line charts
n_data = []
p_data = []
k_data = []

font = pygame.font.SysFont('Arial', 8)

def draw_label(parameter_name, value, position):
    text = font.render(f'{parameter_name}: {value:.1f}', True, BLACK)
    screen.blit(text, position)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)

    # Draw the labels and half donut charts
    draw_label('Temperature', sensor_data['temperature'], (10, 10))
    draw_half_donut_chart(sensor_data['temperature'], 100, RED, (10, 30), 'Temperature')

    draw_label('Humidity', sensor_data['humidity'], (110, 10))
    draw_half_donut_chart(sensor_data['humidity'], 100, BLUE, (110, 30), 'Humidity')

    draw_label('PH', sensor_data['ph'], (210, 10))
    draw_half_donut_chart(sensor_data['ph'], 14, GREEN, (210, 30), 'PH')

    # Update and draw the labels and line charts
    n_data.append(sensor_data['n'])
    p_data.append(sensor_data['p'])
    k_data.append(sensor_data['k'])

    draw_label('N', sensor_data['n'], (10, 130))
    draw_line_chart(n_data, PURPLE, (10, 150))

    draw_label('P', sensor_data['p'], (110, 130))
    draw_line_chart(p_data, YELLOW, (110, 150))

    draw_label('K', sensor_data['k'], (210, 130))
    draw_line_chart(k_data, CYAN, (210, 150))

    pygame.display.flip()
    pygame.time.wait(2000)

pygame.quit()
