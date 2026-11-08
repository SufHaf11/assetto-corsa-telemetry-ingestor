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
        print(udp_socket.recvfrom(1024))
except KeyboardInterrupt:
    print("\n- Telemetry ingestor stopped. -")
    udp_socket.close()

