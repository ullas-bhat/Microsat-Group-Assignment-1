# Implemented for windows line ending and command prompt window
# Input arguments:
# -l: log file name and location (default: GPS_LOG\log.csv)

# Uses only GPS satellites

# Importing the required modules
import serial
import os
import sys
import time
import pandas as pd

# Class for storing the GNSS receiver output data
class receiver_messages:
    # Initializing the required variables
    def __init__(self, serial_instance):
        self.serial_instance = serial_instance  # serial instance used for communication
        self.fix_status = "No fix"              # fix status (No fix, 2D fix, 3D fix)
        self.pdop = 0.0                         # PDOP
        self.hdop = 0.0                         # HDOP
        self.vdop = 0.0                         # VDOP
        self.latitude = "0.000000 N"            # Latitude [deg]
        self.longitude = "0.000000 E"           # Longitude [deg]
        self.altitude = "0.0 m"                 # Altitude [m]
        self.direction = "000.0"                # Direction [deg]
        self.speed = "000.0 kn"                 # Speed [kn]
        self.utc_hours = "00"                   # UTC hour
        self.utc_minutes = "00"                 # UTC minute
        self.utc_seconds = "00.000"             # UTC second
        self.utc_time = "00:00:00.000"          # UTC time [hh:mm:ss.sss]
        self.utc_day = "01"                     # UTC day [1-31]
        self.utc_month = "01"                   # UTC month [1-12]
        self.utc_year = "1980"                  # UTC year
        self.utc_date = "01/01/1960"            # UTC date [dd/mm/yyyy]
        self.gps_satellites = []                # GPS satellites in view; [0]:Sat no; [1]:Sat el; [2]:Sat az; [3]:Sat SNR
        self.gps_satellites_used = ""           # GPS satellites used for fix
        self.running = True                     # bool value used to store state of reading
        self.history = []                       # list for logging

    # Function to read the NMEA message from the serial link
    def get_raw_messages(self):
        message = str(self.serial_instance.readline())
        message = message[2:len(message)-1]
        return message
    
    # Function to read and parse NMEA messages. Returns 1 if the message was parsed and its data used. Returns 0 if the message type is not implemented
    # Implemented message types: $GPGGA, $GNGSA, $GPGSV, $GNRMC, $GNZDA
    def parse_message(self):
        # Get raw message
        message = self.get_raw_messages()
        message = message.split(sep=',')

        # $GPGGA message decoding (location)
        if message[0] == '$GPGGA':
            self.latitude = str(float(message[2][0:2]) + float(message[2][2:])/60) + ' ' + message[3]
            self.longitude = str(float(message[4][0:3]) + float(message[4][3:])/60) + ' ' + message[5]
            self.altitude = message[9] + ' m'
            return 1

        # $GNGSA message decoding (fix status and satellites used)
        elif message[0] == '$GNGSA':
            if message[2] == '1':
                self.fix_status = "No fix"
            elif message[2] == '2':
                self.fix_status = "2D fix"
            elif message[2] == '3':
                self.fix_status = "3D fix"
            else:
                self.fix_status = "Invalid fix data"

            self.pdop = message[15]
            self.hdop = message[16]
            self.vdop = message[17]
            
            if message[3] == '':
                return 1
            else:
                self.gps_satellites_used = []
                i = 3
                while message[i] != '':
                    self.gps_satellites_used.append(message[i])
                    i += 1
                self.gps_satellites_used = self.gps_satellites_used[0:len(self.gps_satellites_used)-2]
                return 1
        
        # $GPGSV message decoding (Info of all satellites in view)
        elif message[0] == '$GPGSV':

            if message[-1][0] == '6':
                return 0
            else:
                self.gps_satellites = []
                sat_info_messages = [message]
                while message[1] != message[2]:
                    message = self.get_raw_messages()
                    message = message.split(sep=',')
                    sat_info_messages.append(message)

                for sat_message in sat_info_messages:
                    i = 4
                    while sat_message[i][1] != '*':
                        sat_num = sat_message[i]
                        sat_el = sat_message[i+1]
                        sat_az = sat_message[i+2]
                        if sat_message[i+3] == '':
                            sat_snr = "--"
                        else:
                            sat_snr = sat_message[i+3]
                        self.gps_satellites.append([sat_num, sat_el, sat_az, sat_snr])
                        i += 4
            return 1     

        # $GNRMC message decoding (speed and direction)
        elif message[0] == '$GNRMC':
            self.speed = message[7] + ' kn'
            self.direction = message[8]
            return 1

        # $GNZDA message decoding (UTC time and date)
        elif message[0] == '$GNZDA':
            self.utc_hours = message[1][0:2]
            self.utc_minutes = message[1][2:4]
            self.utc_seconds = message[1][4:10]
            self.utc_time = self.utc_hours + ':' + self.utc_minutes + ':' + self.utc_seconds

            self.utc_day = message[2]
            self.utc_month = message[3]
            self.utc_year = message[4]
            self.utc_date = self.utc_day + '/' + self.utc_month + '/' + self.utc_year 
            return 1

        return 0
    
    # Function to update log file. Currently logging UTC time, latitude, longitude, fix status, PDOP, HDOP and VDOP
    def update_log(self):
        self.history.append([self.utc_time, self.latitude, self.longitude, self.fix_status, self.pdop, self.hdop, self.vdop])


    # Updating terminal screen
    def update_screen(self):
        os.system('cls')
        print(f"UTC Time: {self.utc_time}\tUTC Date: {self.utc_date}")
        print(f"Fix status: {self.fix_status}\tPDOP: {self.pdop}\tHDOP: {self.hdop}\tVDOP: {self.vdop}")
        print(f"Latitude: {self.latitude}\t\tLongitude: {self.longitude}\t\tAltitude: {self.altitude}")
        print(f"Direction: {self.direction}\t\t\tSpeed: {self.speed}")

        print(f"\n\nGPS satellites used for fix: {self.gps_satellites_used}")
        print("\n\nGPS satellites in view:")
        try:
            for satellite in self.gps_satellites:
                print(f"Sat no: {satellite[0]}\t\tEl: {satellite[1]}\t\tAz: {satellite[2]}\t\tSNR: {satellite[3]}")
        except IndexError:
            print(" ")


# Function to check avilable ports
def check_open_ports():
    ports = ['COM%s' % (i + 1) for i in range(256)]
    output = []

    for port in ports:
        try:
            serial_check = serial.Serial(port)
            serial_check.close
            output.append(port)

        except serial.SerialException :
            continue
    
    return output


# Function to display start screen to set COM port and Baud rate
def start_screen(com_port, baud_rate, display_message = True, start_selection='n'):
    if display_message:
        print(f"Default Parameters:\nCOM Port:\t{com_port}\nBaud Rate:\t{baud_rate}")
        start_selection = input("Continue with default connection parameters? [y/n]: ")

    if start_selection == 'n' or start_selection == 'N':
        available_ports = check_open_ports()
        print(f"Available ports: {available_ports}")
        com_port = input("Enter COM port (ex: COM16): ")
        com_check = com_port[0:3]
        if com_check != 'COM':
            print("Invalid COM port")
            return start_screen(com_port, baud_rate, display_message=False)
        try:
            serial_check = serial.Serial(com_port)
            serial_check.close
        except serial.SerialException:
            print("COM port not avilable, try different COM port")
            return start_screen(com_port, baud_rate, display_message=False)

        baud_rate = input("Enter Baud rate: ")
        return com_port, baud_rate

    elif start_selection == 'y' or start_selection == 'Y':
        try:
            serial_check = serial.Serial(com_port)
            serial_check.close
        except serial.SerialException:
            print("COM port not avilable, try different COM port")
            return start_screen(com_port, baud_rate, display_message=False)
        return com_port, baud_rate
    
    else:
        print("Invalid selection")
        return start_screen(com_port, baud_rate, display_message=False)


# Function to start collecting GPS messages
def start_messages():
    start_selection = input("Start GPS Monitoring? [y/n]: ")

    if start_selection == 'n' or start_selection == 'N':
        print("Quiting program")
        exit()
    
    elif start_selection == 'y' or start_selection == 'Y':
        os.system('cls')
    
    else:
        print("Invalid selection")
        start_messages()


if __name__ == '__main__':
    # Setting log file location
    args = sys.argv
    if len(args) > 2:
        if args[1] == '-l':
            log_file = args[2]
    else:
        log_file = r"GPS_LOG\log.csv"

    # Start screen
    baud_rate = 115200
    com_port = 'COM16'
    os.system('cls')
    com_port, baud_rate = start_screen(com_port, baud_rate, start_selection='')
    print(f"COM Port: {com_port}\tBaud Rate: {baud_rate}")
    print("\n\n")
    start_messages()

    serial_instance = serial.Serial(com_port, baud_rate, timeout=1) # Opening serial port
    gps_receiver = receiver_messages(serial_instance)   # Creating an instance of the receiver_messages class

    # Command to cold-start the GNSS receiver at the beginning
    cold_start = [0xA0, 0xA1, 0x00, 0x0F, 0x01, 0x03, 0x07, 0xD8, 0x0B, 0x0E, 0x08, 0x2E, 0x03, 0x09, 0xC4, 0x30, 0x70, 0x00, 0x64, 0x14, 0x0D, 0x0A]
    cold_start_bytes = bytearray(cold_start)
    #gps_receiver.serial_instance.write(cold_start_bytes)

    # Keeping track of last screen and log update time
    last_update = time.time()

    try:
        while gps_receiver.running:
            gps_receiver.parse_message()    # Reading and parsing message
            if time.time() - last_update > 1:   # Updating screen and log file
                gps_receiver.update_screen()
                gps_receiver.update_log()
    
    except KeyboardInterrupt:
        # Script end routine
        gps_receiver.running = False
        data_frame = pd.DataFrame(gps_receiver.history, columns=['UTC Time', 'Latitude', 'Longitude', 'Altitude'])
        data_frame.to_csv(log_file, index=False)
        serial_instance.close

        print("Stopping program")

