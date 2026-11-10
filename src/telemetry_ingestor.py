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
print("- Listening for data... -")


#Formats the gear value to display neutral and reverse as N or R instead of integer values like 1 or 0. Makes the ouput more readable
def format_gear(gear):
    if gear == 1:
        return "N"
    elif gear == 0:
        return "R"
    else:
        return str(gear)

#Loops indefinitely to receive telemetry data from Assetto Corsa and print it to the console until a interrupt
try:
    while True:
# Capture raw bytes from the data stream
        data, addr = udp_socket.recvfrom(1024)

#Assetto corsa only uses 328 bytes so a check is done to ensure the data is the correct size before unpacking the bytes
#Assetto corsa sends data in 4 bytes values so unpacking for each value is done with .unpack and in 4 byte increments. The game also required a 4 byte buffer to allow it to be unpacked correctly.     
        if len(data) == 328:

                #Bytes from the data stream are unpacked and assigned values to the respective variables.
                speed = struct.unpack('<8xf', data[:12])[0]
                #<8xf unpacks 8 bytes (2*4 bytes) and skips the first 8 bytes of the data stream to get to the speed value which is located at byte 8-12. The f indicates that the value is a float.
                
                #RPM bytes
                rpm = struct.unpack('<68xf', data[:72])[0]

                #Selected gear bytes
                gear = struct.unpack('<76xi', data[:80])[0]

                #Outputs the telemtry data in a readable format without constant outputs. Values are flushed to the console to ensure they are printed immediately and not buffered.
                print(f"\rRPM: {rpm:6.0f} | Speed: {speed:6.2f} km/h | Selected Gear: {format_gear(gear)}", end="", flush=True)



except KeyboardInterrupt:
    print("\nTelemetry ingestor stopped.")
    udp_socket.close()

