import serial
import threading
import time
from datetime import datetime
import re

class SerialReader:

    def thread_function(self):
        break_chars = ["\r", "\n"]

        while True:
            if (self.connected):
                self.ser.write(b'D')
                line = ""
                while True:
                    car = self.ser.read(1)
                    if( car == b'\x00' ):
                        continue
                    line += car.decode("ISO-8859-1")
                    if len(line) == 0 or line[-1] in break_chars:
                        break
                if (len(line) > 1):
                    line = line[:-1].replace(',', '.')
                    matches = re.match( r"^([A-Za-z\s]+)(\-?[\d\.]+)([^\d\.].*)$", line )
                    if( matches ):
                        newData = ( datetime.now(), float( matches.groups()[1] ), matches.groups()[2].strip() + " (" +  matches.groups()[0].strip() + ")" )
                    else:
                        newData = ( datetime.now(), 0, line )

                    self.newData.append( newData )
                    self.saver.stream_data( *newData )

            time.sleep(0.1)

    def __init__(self, saver):
        self.connected = False
        self.thread = threading.Thread(target=self.thread_function)
        self.thread.start()
        self.data = []
        self.newData = []
        self.saver = saver

    def connect(self, port):
        self.ser = serial.Serial(port,baudrate=1200,bytesize=serial.SEVENBITS,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_TWO)
        self.ser.setDTR(1)
        self.ser.setRTS(0)

        self.connected = True

    def close(self):
        self.connected = False
        self.ser.close()

    def newData(self):
        return len( self.newData ) > 0

    def flushData( self ):
        self.data = [ *self.data, *self.newData ]
        self.newData = []

    def getAllData(self):
        if( self.newData ):
            self.flushData()
        return self.data
    
    
    def getLastData(self):
        if( len( self.newData ) > 0 ):
            return ( self.newData[-1][0], self.newData[-1][1], self.newData[-1][2] )
        if( len( self.data ) > 0 ):
            return ( self.data[-1][0], self.data[-1][1], self.data[-1][2] )
        return ( datetime.now(), 0, "No data" )

    def getNewData(self):
        toReturn = self.newData[:]
        self.flushData()
        return toReturn

    def makeDisplayableData(self, data):
        return "\n".join([f"{d[0].strftime('%H:%M:%S')}\t{d[1]}\t{d[2]}" for d in data])
