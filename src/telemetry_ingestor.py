import socket
import struct 
import asyncio
import websockets
import json
from parser import parse_handshake, parse_telemetry #Importing the parse handshake and telemetry from the parser script

#Change target host IP if you are using a different machine to send the telemetry data
HOST = "127.0.0.1"
PORT = 9996

#Change the websocket host and port if you want to use a different machine to receive the telemetry data
WS_HOST = "localhost"
WS_PORT = 8765
connected_clients = set()

#Create the UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


#Listen for the handshake response from Assetto Corsa
sub_packet = struct.pack('<iii', 0, 1, 1)
udp_socket.sendto(sub_packet, (HOST, PORT))
print("- Listening for data... -")


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


            #Uses the parse_telemetry function from the parser script to unpack the raw bytes into a dictionary of telemetry data.
            telemetry_data = parse_telemetry(data)

            #Assetto corsa only uses 328 bytes so a check is done to ensure the data is the correct size before unpacking the bytes
            #Assetto corsa sends data in 4 bytes values so unpacking for each value is done with .unpack and in 4 byte increments. The game also required a 4 byte buffer to allow it to be unpacked correctly.     
            #If the data is not the expected size, it returns None.
            if telemetry_data:
                speed = telemetry_data["speed"]
                rpm = telemetry_data["rpm"] 
                gear = telemetry_data["gear"]
                posx = telemetry_data["posx"]
                posy = telemetry_data["posy"]
                posz = telemetry_data["posz"]
                lastLap = telemetry_data["lastLap"]
                bestLap = telemetry_data["bestLap"]
                lapCount = telemetry_data.get("lapCount", 0)  # Default to 0 if lapCount is not present

                    #If there are connected clients, the data is converted to JSON and sent to the websocket server
                if connected_clients:
                    message = json.dumps(telemetry_data)
                    for client in connected_clients:
                        await client.send(message)
                    
                    #Outputs the telemtry data in a readable format without constant outputs. Values are flushed to the console to ensure they are printed immediately and not buffered.
                    print(f"\rRPM: {rpm:6.0f} | Speed: {speed:6.2f} km/h | Selected Gear: {gear} | Position: ({posx:.0f}, {posy:.0f}, {posz:.0f}) | Last Lap: {lastLap:.0f} | Best Lap: {bestLap:.0f} | Lap Count: {lapCount:.0f}", end="", flush=True)
                    
                    


    except KeyboardInterrupt:
        print("\nTelemetry ingestor stopped.")
        udp_socket.close()


# Start the WebSocket server and keep it running alongside the telemetry loop
async def main():
    async with websockets.serve(ws_handler, WS_HOST, WS_PORT):
        await main_loop()



if __name__ == "__main__":
    asyncio.run(main())
