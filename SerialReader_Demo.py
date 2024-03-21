import serial
import threading
import time
from datetime import datetime
import random
import numpy as np

WindowTitle = "DEMO"
FileExt = "demo"
ProbesCount = 2

class SerialReader:

    def thread_function(self):

        while True:

            newData = (datetime.now(), random.random() * np.exp( - len( self.data ) / 1000 ), 'amoli', - random.random() * np.exp( - len( self.data ) / 1000 ), 'prugne' )

            self.newData.append(newData)
            self.saver.stream_data(*newData)

            time.sleep(0.01)

    def __init__(self, saver):
        self.thread = threading.Thread(target=self.thread_function)
        self.data = []
        self.newData = []
        self.saver = saver
        self.thread.start()

    def connect(self, port):
        pass

    def close(self):
        pass

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
        return "\n".join([d[0].strftime('%H:%M:%S') + "\t" + "{:.2f}".format(d[1]) + "amoli" for d in data])
