import socket
import struct 
import asyncio
import websockets
import json

#Change target host IP if you are using a different machine to send the telemetry data
HOST = "127.0.0.1"
PORT = 9996

#Change the websocket host and port if you want to use a different machine to receive the telemetry data
WS_HOST = "localhost"
WS_PORT = 8765
connected_clients = set()

#Create the UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Create the handshake packet and send it to Assetto Corsa
handshake_packet = struct.pack('<iii', 0, 1, 0)
udp_socket.sendto(handshake_packet, (HOST, PORT))
print("- Handshake sent to Assetto Corsa. -")

#Gets the handshake response from the game and unpacks the car and track name from raw bytes.
handshake_data, _ = udp_socket.recvfrom(1024)
if len(handshake_data) == 408:
    #The bytes are decoded from UTF-16 little endian and stripped of null characters to get the actual names
    raw_car_bytes, raw_track_bytes = struct.unpack('<100s108x100s100x', handshake_data)
    car_name = raw_car_bytes.decode('utf-16-le', errors='ignore').strip('\x00')
    track_name = raw_track_bytes.decode('utf-16-le', errors='ignore').strip('\x00')
    print(f"- Car: {car_name} | Track: {track_name} -")
else:
    print(f"- Unexpected handshake packet size: {len(handshake_data)} bytes -")



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
    #Temp fix for gears showing a gear selected higher than it is. Will be fixed properly when fetching car information data
    elif gear >= 2:
        return str(gear - 1)
    
    else:
        return str(gear)

#Tracks the website connects and disconnects
async def ws_handler(websocket):
    connected_clients.add(websocket)
    print(f"\nDashboard connected! Active clients: {len(connected_clients)}")
    
    #Keeps the websocket connection open until the client disconnects.
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)
        print(f"\nDashboard disconnected. Active clients: {len(connected_clients)}")


#Added a function to allow for the data to be sent to a websocket server. The data is converted to JSON and sent to be parsed and translated back on the receiving end.
async def main_loop():
    loop = asyncio.get_running_loop()
    
    #Loops indefinitely to receive telemetry data from Assetto Corsa and print it to the console until a interrupt
    try:
        udp_socket.setblocking(False)

        while True:
            #Waits to capture raw bytes from the data stream to the socket
            data = await loop.sock_recv(udp_socket, 1024)
            
            
   
   
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

                    #Car position bytes. As its a 3D vector, 3 values are unpacked for the x,y and z coordinates
                    posx, posy, posz = struct.unpack('<316x3f', data[:328])   

                    #Dictionary for the data to be converted to JSON and sent to the websocket.
                    telemetry_data = {
                        "speed": speed,
                        "rpm": rpm,
                        "gear": format_gear(gear),
                        "posx": posx,
                        "posy": posy,
                        "posz": posz
                    }

                    if connected_clients:
                        message = json.dumps(telemetry_data)
                        for client in connected_clients:
                            await client.send(message)
                    
                    #Outputs the telemtry data in a readable format without constant outputs. Values are flushed to the console to ensure they are printed immediately and not buffered.
                    print(f"\rRPM: {rpm:6.0f} | Speed: {speed:6.2f} km/h | Selected Gear: {format_gear(gear)} | Position: ({posx:.0f}, {posy:.0f}, {posz:.0f})", end="", flush=True)
                    
                    


    except KeyboardInterrupt:
        print("\nTelemetry ingestor stopped.")
        udp_socket.close()

async def main():
    # Start the WebSocket server and keep it running alongside the telemetry loop
    async with websockets.serve(ws_handler, WS_HOST, WS_PORT):
        await main_loop()





if __name__ == "__main__":
    asyncio.run(main())
