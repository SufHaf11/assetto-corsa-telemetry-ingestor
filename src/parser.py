import struct

HANDSHAKE_SIZE = 408
TELEMETRY_SIZE = 328

#Decodes a raw byte string from Assetto Corsa into a human-readable string, removing any null bytes and ignoring any errors in the decoding process.
def decode_ac_string(raw_bytes: bytes) -> str:
    text = raw_bytes.decode("utf-16-le", errors="ignore")
    text = text.split("%", 1)[0]
    return text.split("\x00", 1)[0]

#Parses the handshake data received from Assetto Corsa and returns a dictionary containing the car name, driver name, track name, and track configuration. If the data is not the expected size, it returns None.
def parse_handshake(data: bytes) -> dict[str, str] | None:
    if len(data) != HANDSHAKE_SIZE:
        return None

    raw_car, raw_driver, raw_track, raw_config = struct.unpack("<100s100s8x100s100s", data)
    return {
        "car_name": decode_ac_string(raw_car),
        "driver_name": decode_ac_string(raw_driver),
        "track_name": decode_ac_string(raw_track),
        "track_config": decode_ac_string(raw_config),
    }

#Formats the gear value to display neutral and reverse as N or R instead of integer values like 1 or 0. Makes the ouput more readable
def format_gear(gear: int) -> str:
    if gear == 1:
        return "N"
    if gear == 0:
        return "R"
    if gear >= 2:
        return str(gear - 1)
    return str(gear)

#Parses the telemetry data received from Assetto Corsa and returns a dictionary containing various telemetry values such as speed, rpm, gear, throttle, brake, clutch, position coordinates, last lap time, best lap time, and lap count.
#If the data is not the expected size, it returns None.
def parse_telemetry(data: bytes) -> dict | None:
    if len(data) != TELEMETRY_SIZE:
        return None

    speed = struct.unpack("<8xf", data[:12])[0]
    rpm = struct.unpack("<68xf", data[:72])[0]
    gear = struct.unpack("<76xi", data[:80])[0]
    throttle, brake, clutch = struct.unpack("<56x3f", data[:68])
    posx, posy, posz = struct.unpack("<316x3f", data[:328])
    last_lap, best_lap, lapCount = struct.unpack("<44x3i", data[:56])

    return {
        "speed": speed,
        "rpm": rpm,
        "gear": format_gear(gear),
        "throttle": throttle,
        "brake": brake,
        "clutch": clutch,
        "posx": posx,
        "posy": posy,
        "posz": posz,
        "lastLap": last_lap,
        "bestLap": best_lap,
        "lapCount": lapCount
    }