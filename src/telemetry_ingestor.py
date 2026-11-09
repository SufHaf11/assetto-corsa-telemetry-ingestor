import socket
import struct 

#Change target host IP if you are using a different machine to send the telemetry data
HOST = "127.0.0.1"
PORT = 9996

#Create the UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Create the handshake packet and send it to Assetto Corsa
handshake_packet = struct.pack('<iii', 0, 1, 0)
udp_socket.sendto(handshake_packet, (HOST, PORT))
print("- Handshake sent to Assetto Corsa. -")

#Listen for the handshake response from Assetto Corsa
sub_packet = struct.pack('<iii', 0, 1, 1)
udp_socket.sendto(sub_packet, (HOST, PORT))
print("- Subscribed to live stream. Listening for data... -")


#Loops indefinitely to receive telemetry data from Assetto Corsa and print it to the console until a interrupt
try:
    while True:
# Capture raw bytes from the data stream
        data, addr = udp_socket.recvfrom(1024)

#Assetto corsa only uses 328 bytes so a check is done to ensure the data is the correct size before unpacking the bytes
#Assetto corsa sends data in 4 bytes values so unpacking for each value is done with .unpack and in 4 byte increments. The game also required a 4 byte buffer to allow it to be unpacked correctly.     
        if len(data) == 328:
            #Currently only speed is being unpacked and printed to the console for testing   
            speed = struct.unpack('<8xf', data[:12])[0]
            #<8xf unpacks 8 bytes (2*4 bytes) and skips the first 8 bytes of the data stream to get to the speed value which is located at byte 8-12. The f indicates that the value is a float.
            print(f"Speed: {speed:.2f} km/h")
            
        



except KeyboardInterrupt:
    print("\nTelemetry ingestor stopped.")
    udp_socket.close()

