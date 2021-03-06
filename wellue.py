import sys
import libscrc
import bluepy
from array import *
import numpy as np
from numpy import ndarray
spo2 = []
data_avg = []
count=0
stream = bytearray()



class MyDelegate(bluepy.btle.DefaultDelegate):
    def __init__(self):
        bluepy.btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        stream.extend(bytearray(data))
        while(True):
            if(len(stream) == 0):
                break
            # search for sync sequence
            idx = stream.find(b'\xaa\x55')
            # gather more bytes if the sync sequence not found
            if(idx < 0):
                break
            # check if there are enough bytes to read the message length
            # otherwise skip and gather more bytes
            if(len(stream) >= idx + 4):
                length = stream[idx + 3]
                # check whether all the bytes of the message available
                # otherwise skip and gather more bytes
                if(len(stream) >= idx + 4 + length):
                    # remove the bytes from the stream prior sync
                    # (if any - as this should not happen except in case of the firs message)
                    del stream[0 : idx]
                    # copy the whole message 
                    message = stream[0 : idx + 4 + length]
                    # the last byte of the message is a CRC8/MAXIM 
                    # the CRC sum for the whole message (including the CRC) must be 0
                    if(libscrc.maxim8(message) != 0):
                        print("CRC error")
                    # remove the sync bytes and the CRC
                    message =  message[2 : idx + 3 + length]
                    # remove the processed bytes from the stream
                    del stream[0 : idx + 4 + length]
                    # messages with 0x08 on the second spot contains values appear on the OLED display
                    if(message[2] == 0x01):
                        if(message[3] != 0):
                                print("SpO2: %d PR: %d PI: %1.1f" % (message[3], message[4], message[6]/10))
                                spo2.append([message[3], message[4], message[6]/10])
                                print(spo2)
                                data_avg = np.mean(spo2, axis=0)
                                print(data_avg)

                                
                                
                            
                        else:
                            break

                else:
                    break
            else:
                break
pulseoximeter = bluepy.btle.Peripheral("cc:f4:82:2f:d4:3e", "random")
if __name__ == "__main__":
   

    # enable notification
    setup_data = b"\x01\x00"
    notify = pulseoximeter.getCharacteristics(uuid='6e400003-b5a3-f393-e0a9-e50e24dcca9e')[0]
    notify_handle = notify.getHandle() + 1
    pulseoximeter.writeCharacteristic(notify_handle, setup_data, withResponse = True)

    while (True):
        if pulseoximeter.waitForNotifications(1.0):
            continue

