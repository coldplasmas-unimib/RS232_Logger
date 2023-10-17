import os
from os.path import exists
import re

class Saver:

    def __init__( self ):
        self.basename = os.getcwd()
        self.file = None
    
    @staticmethod
    def clean_foldername( foldername ):
        return re.sub( r'[^a-zA-Z0-9_-]', '', foldername )
    
    def compute_foldername( self, subfolder ):
        return self.basename + "/" + self.clean_foldername( subfolder )

    def make_filename( self, folder, progr ):
        return folder + "/M" + "{:04d}".format(progr) + ".metex.csv"

    def compute_filename( self, subfolder ):
        folder = self.compute_foldername( subfolder )
        os.makedirs( folder, exist_ok=True )

        progr = 0
        while( exists( self.make_filename( folder, progr ) ) ):
            progr += 1

        return self.make_filename( folder, progr )
    
    def start_saving( self, subfolder ):
        saving_on = self.compute_filename( subfolder )
        self.file = open( saving_on, 'w', buffering = 1 )
        return saving_on
    
    def stream_data( self, datetime, data, udm ):
        if( self.file ):
            self.file.write( "{:.0f}".format(datetime.timestamp()*1000) + "," + str(data) + ","  + str(udm) + "\n" )

    def stop_saving( self ):
        self.file.close()
        self.file = None

    def is_saving( self ):
        return not not self.file
