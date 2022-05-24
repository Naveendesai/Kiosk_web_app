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
            
            idx = stream.find(b'\xaa\x55')

            if(idx < 0):
                break

            if(len(stream) >= idx + 4):
                length = stream[idx + 3]
              
                if(len(stream) >= idx + 4 + length):
                    
                    del stream[0 : idx]
                    
                    message = stream[0 : idx + 4 + length]
                   
                    if(libscrc.maxim8(message) != 0):
                        print("CRC error")
                   
                    message =  message[2 : idx + 3 + length]
                  
                    del stream[0 : idx + 4 + length]
                    
                    if(message[2] == 0x01):
                        global data_avg
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
            return(data_avg)

def pulseoximeter():
    pulseoximeter = bluepy.btle.Peripheral("cc:f4:82:2f:d4:3e", "random")
    try:
        pulseoximeter.setDelegate(MyDelegate())

        # enable notification
        setup_data = b"\x01\x00"
        notify = pulseoximeter.getCharacteristics(uuid='6e400003-b5a3-f393-e0a9-e50e24dcca9e')[0]
        notify_handle = notify.getHandle() + 1
        pulseoximeter.writeCharacteristic(notify_handle, setup_data, withResponse = True)

        
        global count
        while True:
            if(count > 150):
                print("Remove finger")
                SPo2 = data_avg[0]
                HR = round(data_avg[1], 2)
                PI = round(data_avg[2], 2)
                break
            else:
                count += 1
                if pulseoximeter.waitForNotifications(1.0):
                    continue

    except bluepy.btle.BTLEDisconnectError:
        pass
