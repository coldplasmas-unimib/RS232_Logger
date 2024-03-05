import serial
import threading
import time
from datetime import datetime
import re

WindowTitle = "Ozone sensors"
FileExt = "ozone"
ProbesCount = 2

class SerialReader:

    def thread_function(self):
        break_chars = ["\r", "\n"]

        while True:
            if (self.connected):
                line = ""
                while True:
                    line += self.ser.read(1).decode("utf-8")
                    if len(line) == 0 or line[-1] in break_chars:
                        break
                if (len(line) > 1):
                    data = line.split(',')
                    if (len(data) != 8):
                        continue
                    try:
                        newData = (datetime.now(), min( float( data[2] ), 10000), 'ppm', min( float( data[6] ), 10000 ), 'ppb' )
                    except ValueError as e:
                        newData = (datetime.now(), 0, 'ppm', 0, 'ppb' )
                    
                    print( line )

                    self.newData.append(newData)
                    self.saver.stream_data(*newData)

            time.sleep(0.1)

    def __init__(self, saver):
        self.connected = False
        self.thread = threading.Thread(target=self.thread_function)
        self.thread.start()
        self.data = []
        self.newData = []
        self.saver = saver

    def connect(self, port):
        self.ser = serial.Serial(baudrate=9600, bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
        self.ser.port = port
        self.ser.open()

        self.connected = True

    def close(self):
        self.connected = False
        self.ser.close()

    def newData(self):
        return len(self.newData) > 0

    def flushData(self):
        self.data = self.data + self.newData
        self.newData = []

    def getAllData(self):
        if (self.newData):
            self.flushData()
        return self.data

    def getNewData(self):
        toReturn = self.newData[:]
        self.flushData()
        return toReturn

    def getLastData(self):
        if (len(self.newData) > 0):
            return self.newData[-1]
        if (len(self.data) > 0):
            return self.data[-1]
        return (datetime.now(), 0, 'ppm', 0, 'ppb')

    def makeDisplayableData(self, data):
        return "\n".join([d[0].strftime('%H:%M:%S') + "\t" + "{:.2f}".format(d[1]) + "ppm\t" + "{:.2f}".format(d[3]) + "ppb\t" for d in data])
