from flask import Flask, jsonify, render_template
import serial
import serial.tools.list_ports
import struct
import time
import threading

app = Flask(__name__)

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
        except Exception as e:
            print(f"Error reading from port {port}: {e}")
        time.sleep(2)  # Wait for 2 seconds before the next read

# Route to serve sensor data as JSON
@app.route('/api/sensor_data')
def get_sensor_data():
    return jsonify(sensor_data)

# Route to display the web page
@app.route('/')
def index():
    return render_template('index.html')

# Start the sensor reading in a separate thread
if __name__ == "__main__":
    port_name = 'COM3'  # Change this to your port name
    threading.Thread(target=continuous_read, args=(port_name,)).start()
    app.run(host='0.0.0.0', port= 5000, debug=True)