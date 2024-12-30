# NPK Soil Monitoring System

The **NPK Soil Monitoring System** is an innovative Internet of Things (IoT)-based solution designed to monitor and analyze soil conditions in real-time. By leveraging advanced sensors and a Raspberry Pi, this system measures critical soil parameters like temperature, humidity, pH, nitrogen (N), phosphorus (P), and potassium (K) levels. This data is continuously collected, analyzed, and displayed on both a local Raspberry Pi display and a remote web UI, providing actionable insights for modern agriculture.

## Key Features:
- **Real-Time Sensor Readings:** The system uses a CWT-NPK soil sensor to measure essential soil parameters, helping users make informed decisions about soil health and crop needs.
- **IoT Connectivity:** Data from the sensors is transmitted to an online MongoDB database, enabling easy access and long-term storage for analysis and comparison across different fields and time periods.
- **Web Interface:** The web UI displays live sensor data for temperature, humidity, pH, and NPK levels. It is designed to be user-friendly, allowing easy monitoring of soil health from any device with a web browser.
- **Local Display Interface:** The Raspberry Pi features a 3.4-inch display that shows real-time data in a compact and easily readable format, making it ideal for on-site monitoring.
- **Data Visualization:** The system utilizes Pygame to display the collected data on the Raspberry Pi in a visually appealing and informative manner.
- **Cloud Integration:** Sensor readings are synced with an online MongoDB database, allowing for remote access and ensuring data integrity and backup.
- **User-Friendly UI:** The web and local UIs are designed to present the data clearly, providing users with immediate insights into the soil’s health.

## System Components:
- **Raspberry Pi:** The heart of the system, providing computing power and display capabilities for both local data visualization and IoT connectivity.
- **CWT-NPK Soil Sensor:** A sensor that measures soil temperature, humidity, pH, and NPK (nitrogen, phosphorus, and potassium) levels, providing vital information for agricultural applications.
- **MongoDB Database:** The database stores sensor data in real-time, enabling easy retrieval for analysis and long-term monitoring.
- **Web Interface (Flask-based):** A web application built with Flask that displays the real-time sensor data, making it accessible from any device on the local network or over the internet.

## Benefits for Agriculture:
- **Optimized Crop Growth:** By regularly monitoring soil conditions, farmers can adjust irrigation, fertilization, and other practices to optimize crop growth.
- **Water and Resource Conservation:** With accurate and timely data on soil moisture and nutrient levels, farmers can reduce water and fertilizer usage, contributing to more sustainable farming practices.
- **Increased Yield:** By ensuring that soil conditions are always at their best, farmers can increase crop yield and improve overall soil health.
- **Ease of Use:** The web and local display interfaces make it easy for users to understand and react to soil data, even with minimal technical knowledge.

## Visuals:
- **System Schematic:**  
  ![Schematic](https://github.com/user-attachments/assets/8df979fa-4c62-4fc7-b0ed-181cb1d49e98)  
  A schematic diagram showing the layout and connections of the system's components.

- **Web UI:**  
  ![Website UI](https://github.com/user-attachments/assets/b9e37572-31d5-49cd-af9f-b281ae82d8e9)  
  The web interface displaying the real-time readings of temperature, humidity, pH, and NPK levels.

- **Raspberry Pi Display:**  
  ![Raspberry Pi Display UI](https://github.com/user-attachments/assets/7f0694ef-284e-403b-a7e1-2184248076c4)  
  The local display on the Raspberry Pi showing sensor readings for temperature, humidity, pH, and NPK.

- **Final Product:**  
  ![Final Product](https://github.com/user-attachments/assets/32de5cc7-9d7c-48dc-8a81-2687ded0c58f)  
  A picture of the final product, showcasing the hardware setup and the operational system.

## Final Product:
The **NPK Soil Monitoring System** is designed for versatility and ease of use. Whether you're monitoring a small garden or a large farm, this system provides accurate, real-time insights into the health of your soil. Its compact design and cloud-based data storage ensure that you can access vital information from anywhere at any time.

The system is built to be both cost-effective and highly functional, offering a user-friendly experience for anyone looking to enhance their agricultural practices through modern IoT technology.
