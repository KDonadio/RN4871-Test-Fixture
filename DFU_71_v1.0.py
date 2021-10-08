#--------------------------------------------------
# DFU_71_v1.0.py
#
# This program uses the MCP2221A for USB to RS-232
# bridge functionality. The RN4871 MODE & RST signals
# are also controlled via teh MCP2221A device.
# This simple GUI interface allows the programming
# of the RN4871 or BM71 devices using the bed of nails
# fixture or the TAG Connect cable for in circuit use.
#
# Author: Keith Donadio
# Date  : 9/24/2021
#--------------------------------------------------
import PySimpleGUI as sg
import PyMCP2221A
import time
import serial
import binascii
import os
import serial.tools.list_ports

# -----------------------------------------------
# A few nice GUI color schemes
# sg.theme("NeutralBlue")
# sg.theme("LightGrey5")
# sg.theme("LightGrey4")
# sg.theme("LightBrown12")
# sg.theme("LightBrown4")
# sg.theme("Kayak")
# sg.theme("GreenTan")
# sg.theme("DarkGreen6")
# sg.theme("DarkBrown6")
# sg.theme("DarkBrown3")
# sg.theme("DarkBlue3")
# sg.theme("DarkBlue13")
# sg.theme("BrownBlue")       # Default color scheme

#-------------------------------------------------
# USB VID & PID for auto detection of COM port
VID = 0x04D8
PID = 0x00DD

#--------------------------------------------------
# Initialize MCP2221A
gpio = PyMCP2221A.PyMCP2221A()
gpio.Reset()
gpio = PyMCP2221A.PyMCP2221A()
gpio.GPIO_Init()
gpio.GPIO_0_OutputMode()
gpio.GPIO_1_OutputMode()
gpio.GPIO_2_OutputMode()
gpio.GPIO_3_OutputMode()
gpio.GPIO_0_Output(0)   # MODE pin
gpio.GPIO_1_Output(0)   # RST pin
gpio.GPIO_2_Output(0)   # LED Green pin
gpio.GPIO_3_Output(0)   # LED Red pin
print_debug = 1

#--------------------------------------------------
# Figure out what COM port device is attached to
def find_serial_port(vid, pid):
        """
        Find a serial port by VID, PID and text name

        :param vid: USB vendor ID to locate
        :param pid: USB product ID to locate
        :param name: USB device name to find where VID/PID match fails

        """
        check_for = "USB VID:PID={vid:04x}:{pid:04x}".format(vid=vid, pid=pid).upper()
        ports = serial.tools.list_ports.comports()

        for check_port in ports:
            if hasattr(serial.tools, 'list_ports_common'):
                if (check_port.vid, check_port.pid) == (VID, PID):
                    return check_port.device
                continue

            if check_for in check_port[2].upper():      # or name == check_port[1]:
                return check_port[0]
        return None

#     sg.Popup('Serial port error. Please connect device.', no_titlebar=True, background_color='dark red')

#--------------------------------------------------
# Re-route the print to the multiline box
def mprint(*args, **kwargs):
    window['textbox'].print(*args, **kwargs)

#--------------------------------------------------
# Re-route all prints to the window
print = mprint

#--------------------------------------------------
# Puts the RN4871 module into CFG mode
def CFG_Mode():
    gpio.GPIO_0_Output(1)  # Set MODE pin low
    gpio.GPIO_1_Output(1)  # Set RST pin low
    time.sleep(0.1)  # Delay for 100mS
    gpio.GPIO_1_Output(0)  # Set RST pin high

#--------------------------------------------------
# Puts the RN4871 module into APP mode
def APP_Mode():
    gpio.GPIO_0_Output(0)  # Set MODE pin high
    gpio.GPIO_1_Output(1)  # Set RST pin low
    time.sleep(0.1)  # Delay for 100mS
    gpio.GPIO_1_Output(0)  # Set RST pin high

#--------------------------------------------------
# Turn on the Green LED
def LED_Green_On():
    gpio.GPIO_2_Output(1)  # Set LED pin high

#--------------------------------------------------
# Turn off the Green LED
def LED_Green_Off():
    gpio.GPIO_2_Output(0)  # Set LED pin low

#--------------------------------------------------
# Turn on the Red LED
def LED_Red_On():
    gpio.GPIO_3_Output(1)  # Set LED pin high

#--------------------------------------------------
# Turn off the Red LED
def LED_Red_Off():
    gpio.GPIO_3_Output(0)  # Set LED pin low

#--------------------------------------------------
# UART setup
def OpenDUT(Port1, Baudrate, timeout_length):
    try:
        port = serial.Serial(port=Port1, baudrate=Baudrate, rtscts=True, timeout=timeout_length, writeTimeout=0.0)
    except serial.SerialException:
        print('Error opening port !!\a\a\r\n')
        exit(-1)
    return port

#--------------------------------------------------
# Send a packet to the RN487x
def CreateSendPacket(commandList):
    packet = bytearray()
    for commandByte in commandList:
        packet.append(commandByte)
    return packet

#--------------------------------------------------
# Convert HEX file data into an array
def ReadHexFile(fileName):
    bankByteArray = bytearray()

    with open(fileName,'r') as file:
        while True:
            data_line = file.readline()
            if (not data_line) or (data_line[:-1] == ':00000001FF'):
                break

            if print_debug > 3:
                print("Data line read: {} and length: {}".format(data_line, len(data_line)))

            if (data_line[0] == ':') and (data_line[len(data_line)-1] == '\n'):
                expectedLengthDataInLine = int(data_line[1:3],16)
                startAddressDataInLine = data_line[3:7]
                numberOfBytesinDataLine = len(data_line)/2
                if (expectedLengthDataInLine != 32) or (expectedLengthDataInLine != (numberOfBytesinDataLine-6)):
                    #The current line does not have 32 bytes.
                    #Header: 9 (1+2+4+2); checksum: 2 ; '\n': 1 ; total = 12 characters = 6 bytes
                    if data_line[1:9] == '02000004':
                        #This is the first line of the Hex file. This only contains 2 bytes. Can be ignored.
                        bytesCollected = 0
                    if data_line[1:9] != '02000004':
                        if bytesCollected != int(startAddressDataInLine,16) :
                            #The start address does not match the bytes collected so far.
                            # There are missing lines along with some missing characters in the current line.
                            linesMissing = int(((int(startAddressDataInLine, 16)) - bytesCollected)/32)
                            # Add the missing number of lines with 0xFF characters. Each line has 32 bytes.
                            for i in range(0, linesMissing):
                                for j in range(0,32):
                                    bankByteArray.append(int('FF',16))
                                    bytesCollected += 1

                            data_line_bytes = data_line[9:((expectedLengthDataInLine*2)+9)]
                            # Adding missing bytes in the current line
                            characterPosition = 0
                            while characterPosition < expectedLengthDataInLine*2:
                                bankByteArray.append(int(data_line_bytes[characterPosition:characterPosition+2],16))
                                bytesCollected += 1
                                characterPosition += 2
                            while characterPosition < 63:
                                bankByteArray.append(int('FF', 16))
                                bytesCollected += 1
                                characterPosition += 2

                        if bytesCollected == int(startAddressDataInLine,16) :
                            # The current line has less than 32 bytes. But there are no missing lines.
                            data_line_bytes = data_line[9:((expectedLengthDataInLine*2)+9)]
                            characterPosition = 0
                            while characterPosition < expectedLengthDataInLine*2:
                                bankByteArray.append(int(data_line_bytes[characterPosition:characterPosition+2],16))
                                bytesCollected += 1
                                characterPosition += 2
                            while characterPosition < 63:
                                bankByteArray.append(int('FF', 16))
                                bytesCollected += 1
                                characterPosition += 2

                if expectedLengthDataInLine == 32:
                    # The current line does have 32 bytes.
                    if bytesCollected != int(startAddressDataInLine, 16):
                        #There are missing lines before the current line. Need to add those lines with FF characters.
                        linesMissing = int(((int(startAddressDataInLine, 16)) - bytesCollected)/32)
                        for i in range(0, linesMissing):
                            for j in range(0,32):
                                bankByteArray.append(int('FF',16))
                                bytesCollected += 1
                    if bytesCollected == int(startAddressDataInLine, 16):
                        characterPosition = 9                   # Data starts from bit#9. Note indexing starts at 0.
                        while characterPosition < 73:           # There are 64 characters to collect;
                            bankByteArray.append(int(data_line[characterPosition:characterPosition+2],16))
                            bytesCollected += 1
                            characterPosition += 2

    return(bankByteArray, bytesCollected)

#--------------------------------------------------
# Load array with 0xFF
def PackHexArray(data, endingByteNumber):
    bankEndByte = 0xFFFF
    finalByteNumber = endingByteNumber
    for i in range(endingByteNumber,bankEndByte):
        data.append(int('FF',16))
        finalByteNumber += 1
    return data, finalByteNumber

#--------------------------------------------------
# FLASH Write (Bank)
def FlashWriteStart(data, bankNumber):
    ACLDataPacket = [0x02]
    connectionHandle = [0xFF, 0x0F]  # Connection handle: 0x0FFF
    ACLDataLength = [0x8E, 0x00]  # ACL Data Length: 0x008E (128 bytes of data + 14 bytes of command related bytes)
    ISDAPCommand = [0x11, 0x01]  # Write command: 0x0111
    commandLength = [0x8A, 0x80]  # ISDAP data length = 0x808A (128 bytes of data + 10 bytes of command related bytes, 80 for Write continue)
    memoryType = [0x03, 0x00]  # Memory type = 0x03 (Flash), submemory type = 0x00 (Embedded)
    address = [0x00, 0x00, bankNumber, 0x00]  # Address: 0x00000000
    size = [0x80, 0x00, 0xFF, 0xFF]  # Total data size to be written: 128 bytes; 0x00 00 00 80
    writeDataList = ACLDataPacket + connectionHandle + ACLDataLength + ISDAPCommand + commandLength + memoryType + address + size

    writeCommandList = CreateSendPacket(writeDataList)
    firstWriteSet = data[0:128]
    for dataByte in firstWriteSet:
        writeCommandList.append(dataByte)
    return writeCommandList

#--------------------------------------------------
#
def FlashWriteContinue(data, address128Number):
    ACLDataPacket = [0x02]
    connectionHandle = [0xFF, 0x0F]
    ACLDataLength = [0x84, 0x00]
    ISDAPCommand = [0x01, 0x00]
    ISDAPDataLength = [0x80, 0x80]
    writeContinuePacket = ACLDataPacket + connectionHandle + ACLDataLength + ISDAPCommand + ISDAPDataLength
    writeCommandList = CreateSendPacket(writeContinuePacket)
    startAddress = (address128Number*128)
    writeContinueSet = data[startAddress:(startAddress+128)]
    for dataByte in writeContinueSet:
        writeCommandList.append(dataByte)
    return writeCommandList

#--------------------------------------------------
#
def FlashWriteContinueLast(data):
    ACLDataPacket = [0x02]
    connectionHandle = [0xFF, 0x0F]
    ACLDataLength = [0x84, 0x00]
    ISDAPCommand = [0x01, 0x00]
    ISDAPDataLength = [0x80, 0x00]
    writeContinuePacket = ACLDataPacket + connectionHandle + ACLDataLength + ISDAPCommand + ISDAPDataLength
    writeCommandList = CreateSendPacket(writeContinuePacket)
    startAddress = (511*128)
    writeContinueSet = data[startAddress:(startAddress+128)]
    for dataByte in writeContinueSet:
        writeCommandList.append(dataByte)
    writeCommandList.append(int('FF',16))
    return writeCommandList

#--------------------------------------------------
# Program device
def program_RN487x():
    global print_debug

    #-----------------------------------------
    hex_f1 = values["_HEX_"]                        # get the name of the selected file from GUI
    hex_f2 = hex_f1.replace("H00", "H01")           # change the suffixes
    hex_f3 = hex_f1.replace("H00", "H02")
    hex_f4 = hex_f1.replace("H00", "H03")
    src_path, hex_file_1 = os.path.split(hex_f1)    # remove the front part of the file path
    src_path, hex_file_2 = os.path.split(hex_f2)
    src_path, hex_file_3 = os.path.split(hex_f3)
    src_path, hex_file_4 = os.path.split(hex_f4)
    #-----------------------------------------

    comPort = find_serial_port(VID, PID)    # Find USB COM port
    baudRate = 115200                       # set the baud rate
    file_name1 = hex_file_1                 # RN487x_v1.40_070919.H00
    file_name2 = hex_file_2                 # RN487x_v1.40_070919.H01
    file_name3 = hex_file_3                 # RN487x_v1.40_070919.H02
    file_name4 = hex_file_4                 # RN487x_v1.40_070919.H03

    fileArray = [file_name1, file_name2, file_name3, file_name4]        # save filenames into an array

    BM71Commands = {  1: [0x01, 0x05, 0x10, 0x00],  # Command to Read IS1871 buffer size
        2: [0x01, 0x05, 0x04, 0x0D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],  # Command to create connection
        3: [0x02, 0xFF, 0x0F, 0x07, 0x00, 0x00, 0x01, 0x03, 0x00, 0x03, 0x00, 0x00],                # Command to Unlock memory
        4: [0x02, 0xFF, 0x0F, 0x0E, 0x00, 0x12, 0x01, 0x0A, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}
                # Erase command: Note that the whole memory needs to be erased for DFU.

    BM71ExpectedResponse = {1: '040e0b0105100000013002000a00',
                            2: '040f040001050404030b00ff0f0000000000000100',
                            3: '04130501ff0f010002ff0f0600000102000000',
                            4: '04130501ff0f010002ff0f0e0012010a0000000008000000100000'}

    # changed to 0.01 to speed up the process. It was taking over three minutes, now about 30 seconds.
    Port1 = OpenDUT(comPort, baudRate, 0.01)
#    Port1 = OpenDUT(comPort, baudRate, 0.1)
    # Do not lower the baud rate to anything lower than 0.1. The module will not respond faster than this.

    for commandname in BM71Commands:
        sendCmd = CreateSendPacket(BM71Commands[commandname])
        Port1.write(sendCmd)
        expectedResponseLength = len(BM71ExpectedResponse[commandname])
        lines = Port1.read(expectedResponseLength)
        BM71Response = (binascii.hexlify(lines)).decode()
        if BM71Response == BM71ExpectedResponse[commandname]:
            print("Command {} Works".format(commandname))

    bankNumber = 0

    for eachFile in fileArray:
        print("--------- Loading file: {}  -----------------".format(eachFile))
        data, numberOfBytes = ReadHexFile(eachFile)
        if print_debug > 0:
            print("Number of bytes read: {} and the number of byte in array: {}".format(numberOfBytes, len(data)))
        bankData, finalByteNo = PackHexArray(data, numberOfBytes)

        sendPacket = FlashWriteStart(bankData, bankNumber)
        Port1.write(sendPacket)
        expectedWriteResponse = '04130501ff0f010002ff0f0600110102000000'
        line1 = Port1.read(len(expectedWriteResponse))
        BM71Response = (binascii.hexlify(line1)).decode()
        if BM71Response == expectedWriteResponse:
            print("First write Response for bank {} worked ".format(bankNumber))

        print("Write Continue for Bank {}: ".format(bankNumber))
        for i in range(1,511):
            #-----------------------------------------------------------------------------------------------------------
            # Display a nice progress bar for each HEX file conversion
            sg.one_line_progress_meter(
                'Converting HEX files',
                i + 1,
                511,
                'Programming bank ' + str(bankNumber+1),
                'Programming bank ' + str(bankNumber+1),
                orientation='h',
                bar_color=('#F47264', '#FFFFFF')
            )
            #-----------------------------------------------------------------------------------------------------------
            sendPacket = FlashWriteContinue(bankData,i)
            Port1.write(sendPacket)
            expectedWriteContinueResponse = '04130501ff0f010002ff0f0600010002000000'
            line1 = Port1.read(len(expectedWriteContinueResponse))
            BM71Response = (binascii.hexlify(line1)).decode()
 #           if BM71Response == expectedWriteContinueResponse:      # Do not print this as it just fills the window with numbers
 #               print(i, end = " ")

        sendPacket = FlashWriteContinueLast(bankData)
        if bankNumber == 3:
            sendPacket.pop()
        Port1.write(sendPacket)
        expectedWriteResponse = '04130501ff0f010002ff0f0600010002000000'
        line1 = Port1.read(len(expectedWriteResponse))
        BM71Response = (binascii.hexlify(line1)).decode()
        if BM71Response == expectedWriteResponse:
            print("Last write Response worked for Bank {}".format(bankNumber))

        bankNumber += 1
        print("---------Finished file: {} ---------------------".format(eachFile))

    disconnectCommandList = [0x01, 0x06, 0x04, 0x03, 0xFF, 0x0F, 0x00]      #Command to Disconnect
    disconnectExpectedResponse = '040f040001060404050400ff0f00'
    sendCmd = CreateSendPacket(disconnectCommandList)
    Port1.write(sendCmd)
    lines = Port1.read(len(disconnectExpectedResponse))
    BM71Response = (binascii.hexlify(lines)).decode()
    if BM71Response == disconnectExpectedResponse:
        print("Disconnected. All Done.")

#--------------------------------------------------
# setup window layout
layout = [[sg.Text("Firmware select:")],
          [sg.Text("HEX file : "), sg.Input(key="_HEX_"), sg.FileBrowse(file_types=(("HEX Files", "*.H00"),))],
          [sg.HorizontalSeparator(color='black')],
          [sg.Text(' ' * 15), sg.Button("Program Device"), sg.Text(' ' * 15), sg.Button("Get Version"), sg.Text(' ' * 15), sg.Button("Exit")],
#         --------------------------------------------------------------------------------------
#          Manual control of the CFG & APP signals
#          [sg.Text(' ' * 15), sg.Button("CFG Mode"), sg.Text(' ' * 15), sg.Button("APP Mode")],
#         --------------------------------------------------------------------------------------
#          Test button for testing new ideas :)
#          [sg.Text(' ' * 15), sg.Button("TEST")],
          [sg.HorizontalSeparator(color='black')],
#         --------------------------------------------------------------------------------------
#          Manual control of the status indicator LED
#         [sg.Button("LED Red On"), sg.Button("LED Red Off")],                     # Used to control the status LED - not used yet
#         [sg.Button("LED Green On"), sg.Button("LED Green Off")],                 # Used to control the status LED - not used yet
          [sg.Multiline(size=(500, 10), key='textbox')]]

#--------------------------------------------------
# Create the window
window = sg.Window("RN4871/BM71 Device Firmware Update Tool", layout, size=(600, 300), icon='mchp-logo-round.ico')

#--------------------------------------------------
# Create an event loop
while True:
    event, values = window.read()

    # --------------------------------------------------
    # TEST button
#    if event == "TEST":

    # --------------------------------------------------
    # CFG Mode button
    if event == "CFG Mode":
        CFG_Mode()
    # --------------------------------------------------
    # APP Mode button
    if event == "APP Mode":
        APP_Mode()
    # --------------------------------------------------
    # LED Red On button
    if event == "LED Red On":
        LED_Red_On()
    # --------------------------------------------------
    # LED Red Off button
    if event == "LED Red Off":
        LED_Red_Off()
    # --------------------------------------------------
    # LED Green On button
    if event == "LED Green On":
        LED_Green_On()
    # --------------------------------------------------
    # LED Green Off button
    if event == "LED Green Off":
        LED_Green_Off()
    # --------------------------------------------------
    # Read Version of Module
    if event == "Get Version":
        print("Firmware Version:")
        comPort = find_serial_port(VID, PID)  # Find USB COM port
        s = serial.Serial(port=comPort, baudrate=115200, bytesize=serial.EIGHTBITS,
                          parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                          timeout=0.1, xonxoff=False, rtscts =True, dsrdtr=False)
#       comPort was hard coded here - fixed now
#        s = serial.Serial(port="COM5", baudrate=115200, bytesize=serial.EIGHTBITS,
#                          parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
#                          timeout=0.1, xonxoff=False, rtscts =True, dsrdtr=False)
        APP_Mode()
        time.sleep(0.1)  # Delay for 100mS
        s.write(b"$$$")
        time.sleep(0.1)  # Delay for 100mS
        res = s.readline()
        s.write(b"V\r\n")
        time.sleep(0.1)  # Delay for 100mS
        res = s.readline()
        temp = (res.decode('utf-8'))
        print(temp)
        sg.Popup('RN4871 Firmware Version', temp)
        s.close()
    # --------------------------------------------------
    # Program button
    if event == "Program Device":
        if values["_HEX_"] == "":
            print("No hex file selected")
            sg.PopupOK('Please load HEX file to continue!')
        else:
            LED_Red_On()
            CFG_Mode()
            time.sleep(0.1)  # Delay for 100mS
            program_RN487x()
            time.sleep(0.1)  # Delay for 100mS
            APP_Mode()
            LED_Red_Off()
            LED_Green_On()
            sg.Popup('Programming complete.', no_titlebar=True, background_color='dark green')
            time.sleep(0.5)  # Delay for 0.5S
            LED_Green_Off()
    # --------------------------------------------------
    # Exit button    	            
    if event == "Exit" or event == sg.WIN_CLOSED:
        print("Program end . . .")
        break

window.close()



