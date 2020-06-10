#!/usr/bin/python

#open pyaudio and detect violence using sklearn machine learning library.
import pyaudio
import sklearn
from sklearn import tree
import struct
import math
import MySQLdb
import mysql.connector

INITIAL_TAP_THRESHOLD = 0.2
FORMAT = pyaudio.paInt16 
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 2
RATE = 44100  
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
# if we get this many noisy blocks in a row, increase the threshold
OVERSENSITIVE = 15.0/INPUT_BLOCK_TIME                    
# if we get this many quiet blocks in a row, decrease the threshold
UNDERSENSITIVE = 120.0/INPUT_BLOCK_TIME 
# if the noise was longer than this many blocks, it's not a 'tap'
MAX_TAP_BLOCKS = 0.15/INPUT_BLOCK_TIME
amplitude1=''
'''cnx = mysql.connector.connect(user='u876018332_vid', password='yeswecan',
                              host='mysql.hostinger.in',
                              database='u876018332_quick')
                              '''
features=[[0.17,0],[0.20,0],[0.213,0],[0.225,0],[0.252,0],[0.275,0]]
labels=["tap","safe sound","Little bit of noise","Might be violence","Scream","Critical"]



def get_rms( block ):
    # RMS amplitude is defined as the square root of the 
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into 
    # a string of 16-bit samples...

    # we will get one short out for each 
    # two chars in the string.
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count )

class TapTester(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.tap_threshold = INITIAL_TAP_THRESHOLD
        self.noisycount = MAX_TAP_BLOCKS+1 
        self.quietcount = 0 
        self.errorcount = 0

    def stop(self):
        self.stream.close()

    def find_input_device(self):
        device_index = None            
        for i in range( self.pa.get_device_count() ):     
            devinfo = self.pa.get_device_info_by_index(i)   
            print( "Device %d: %s"%(i,devinfo["name"]) )

            for keyword in ["mic","input"]:
                if keyword in devinfo["name"].lower():
                    print( "Found an input: device %d - %s"%(i,devinfo["name"]) )
                    device_index = i
                    return device_index

        if device_index == None:
            print( "No preferred input found; using default input device." )

        return device_index

    def open_mic_stream( self ):
        device_index = self.find_input_device()

        stream = self.pa.open(   format = FORMAT,
                                 channels = CHANNELS,
                                 rate = RATE,
                                 input = True,
                                 input_device_index = device_index,
                                 frames_per_buffer = INPUT_FRAMES_PER_BLOCK)

        return stream

    def tapDetected(self):

        clf=tree.DecisionTreeClassifier()
        clf=clf.fit(features,labels)
        print (clf.predict([[amplitude1,0]]))
        
        #amplitude1
    def listen(self):
        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)
        except IOError:
            # dammit. 
            self.errorcount += 1
            print( "(%d) Error recording: %s"%(self.errorcount,e) )
            self.noisycount = 1
            return
        global amplitude1
        amplitude = get_rms( block )
        amplitude1=amplitude
        
        if amplitude > self.tap_threshold:
            # noisy block
            self.quietcount = 0
            self.noisycount += 1
            if self.noisycount > OVERSENSITIVE:
                # turn down the sensitivity
                #self.tap_threshold *= 1.1
                pass
        else:            
            # quiet block.

            if 1 <= self.noisycount <= MAX_TAP_BLOCKS:
                self.tapDetected()
            self.noisycount = 0
            self.quietcount += 1
            if self.quietcount > UNDERSENSITIVE:
                # turn up the sensitivity
                #self.tap_threshold *= 0.9
                pass

if __name__ == "__main__":
    tt = TapTester()

    for i in range(1200):
        tt.listen()
