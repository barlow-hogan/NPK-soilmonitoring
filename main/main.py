import serial
import struct
import threading
import time
import socket
from pymongo import MongoClient
import pygame

# MongoDB setup
mongo_uri = "mongodb+srv://iqbal1109:1109daksa@npk-readings.1kfyyby.mongodb.net/?retryWrites=true&w=majority&appName=NPK-readings"
client = MongoClient(mongo_uri)
db = client['NPK-readings']
collection = db['sensor_data']

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_info = pygame.display.Info()
WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Sensor Data Visualization')

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

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
    slave_address = 0x01
    function_code = 0x03
    starting_address = 0x0000
    num_registers = 0x0007
    crc = calculate_crc(bytes([slave_address, function_code, starting_address >> 8, starting_address & 0xFF,
                                num_registers >> 8, num_registers & 0xFF]))

    request = bytes([slave_address, function_code, starting_address >> 8, starting_address & 0xFF,
                     num_registers >> 8, num_registers & 0xFF]) + crc

    try:
        with serial.Serial(port, baudrate=4800, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                           stopbits=serial.STOPBITS_ONE, timeout=0.1) as ser:
            ser.write(request)
            response = ser.read(7 * 2 + 5)
    except Exception as e:
        print(f"Error reading from port {port}: {e}")
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    data = response[3:-2]
    values = struct.unpack(f'>{len(data)//2}H', data)

    humidity = values[0] / 10.0
    temperature = values[1] / 10.0
    ph = values[3] / 10.0
    n = values[4] / 10.0
    p = values[5] / 10.0
    k = values[6] / 10.0

    return humidity, temperature, ph, n, p, k

# Function to check internet connection
def check_internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as e:
        print(f"No internet connection: {e}")
        return False

# Function to save data to MongoDB with error handling
def save_to_mongo(data):
    if check_internet():
        try:
            collection.insert_one(data)
            print("Data saved to MongoDB")
        except Exception as e:
            print(f"Error saving data to MongoDB: {e}")
    else:
        print("Skipping data upload due to no internet connection")

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

            log_file_path = r'log/sensor_log.log'
            log_data = f"{time.strftime('%Y-%m-%d %H:%M:%S')}, {temperature:.1f}, {humidity:.1f}, {ph:.1f}, {n:.1f}, {p:.1f}, {k:.1f}\n"
            with open(log_file_path, 'a') as log_file:
                log_file.write(log_data)

            mongo_data = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'temperature': temperature,
                'humidity': humidity,
                'ph': ph,
                'n': n,
                'p': p,
                'k': k
            }
            save_to_mongo(mongo_data)

        except Exception as e:
            print(f"Error in continuous read loop: {e}")
        time.sleep(2)

# Start the sensor reading in a separate thread
port_name = '/dev/ttyUSB0'
threading.Thread(target=continuous_read, args=(port_name,)).start()

# Function to draw a half donut chart
def draw_half_donut_chart(value, max_value, color, position, parameter_name):
    x, y = position
    radius = 40
    thickness = 20
    start_angle = 3.14159
    end_angle = 3.14159 * (1 + (value / max_value))
    pygame.draw.arc(screen, color, [x - radius, y - radius, 2 * radius, 2 * radius], start_angle, end_angle, thickness)
    font = pygame.font.SysFont('Arial', 12)
    text = font.render(f'{parameter_name}: {value:.1f}', True, WHITE)
    text_rect = text.get_rect(center=(x, y + radius + 20))
    screen.blit(text, text_rect)

# Function to draw a line chart
def draw_line_chart(data, color, position, min_value=0, max_value=20, max_length=10):
    x, y = position
    width = 150
    height = 100
    if len(data) > max_length:
        data.pop(0)
    for i in range(len(data) - 1):
        x1 = x + i * (width // (max_length - 1))
        y1 = y + height - int(height * (data[i] - min_value) / (max_value - min_value))
        x2 = x + (i + 1) * (width // (max_length - 1))
        y2 = y + height - int(height * (data[i + 1] - min_value) / (max_value - min_value))
        pygame.draw.line(screen, color, (x1, y1), (x2, y2), 2)

# Initialize data storage for line charts
n_data = []
p_data = []
k_data = []

font = pygame.font.SysFont('Arial', 12)

def draw_label(parameter_name, value, position, centered=False):
    text = font.render(f'{parameter_name}: {value:.1f}', True, WHITE)
    text_rect = text.get_rect(center=position if centered else None)
    screen.blit(text, text_rect if centered else position)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    screen.fill(BLACK)

    # Draw the half donut charts
    draw_half_donut_chart(sensor_data['temperature'], 100, RED, (WIDTH // 6, HEIGHT // 6), 'Temperature')
    draw_half_donut_chart(sensor_data['humidity'], 100, BLUE, (WIDTH // 2, HEIGHT // 6), 'Humidity')
    draw_half_donut_chart(sensor_data['ph'], 14, GREEN, (5 * WIDTH // 6, HEIGHT // 6), 'PH')

    # Update and draw the line charts
    n_data.append(sensor_data['n'])
    p_data.append(sensor_data['p'])
    k_data.append(sensor_data['k'])

    draw_label('N', sensor_data['n'], (WIDTH // 6, HEIGHT // 2), centered=True)
    draw_line_chart(n_data, PURPLE, (WIDTH // 6 - 75, HEIGHT // 2 + 20))

    draw_label('P', sensor_data['p'], (WIDTH // 2, HEIGHT // 2), centered=True)
    draw_line_chart(p_data, YELLOW, (WIDTH // 2 - 75, HEIGHT // 2 + 20))

    draw_label('K', sensor_data['k'], (5 * WIDTH // 6, HEIGHT // 2), centered=True)
    draw_line_chart(k_data, CYAN, (5 * WIDTH // 6 - 75, HEIGHT // 2 + 20))

    pygame.display.flip()

pygame.quit()
