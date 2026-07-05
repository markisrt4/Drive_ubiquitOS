import time
import serial

PORT = "/dev/rfcomm0"
BAUD = 38400

def send(ser: serial.Serial, cmd: str, delay: float = 0.5) -> str:
    ser.write((cmd + "\r").encode("ascii"))
    time.sleep(delay)
    data = ser.read_all().decode("ascii", errors="replace")
    return repr(data)

with serial.Serial(PORT, BAUD, timeout=2) as ser:
    for cmd in ["ATZ", "ATI", "ATE0", "ATL0", "ATS0", "ATH1", "ATSP0", "0100", "010C", "010D", "010B", "0133"]:
        print(cmd, "=>", send(ser, cmd))

