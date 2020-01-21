import serial


class Joystick:
    def __init__(self):
        self.output = ""
        self.port = serial.Serial('COM4', baudrate=9600, timeout=0.01)

    def update_port(self):
        arduino = self.port.readline().decode('ascii')
        self.output = arduino
        if arduino != "":
            print(self.output)
