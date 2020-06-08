import smbus
import time
import json

saidasDigitais = []

for i in range (0, 32):
    saidasDigitais.append (0)
    print (i)
    
print (saidasDigitais)



while (1):

    bus = smbus.SMBus(1)
    
    byte1 = bus.read_byte_data(0x26, 0xFF)
    byte2 = bus.read_byte_data(0x27, 0xFF)
    
    print (bin(byte1))
    print (bin(byte2))
    print ("/////////")
    
    time.sleep (1)
    
    
    '''
    bus.write_byte_data(0x22, 0x00, 0xFF)
    bus.write_byte_data(0x23, 0x00, 0xFF)
    time.sleep (1)
    
    bus.write_byte_data(0x22, 0x00, 0x00)
    bus.write_byte_data(0x23, 0x00, 0x00)
    time.sleep (1)
    '''
    
    