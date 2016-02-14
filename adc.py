from Adafruit.Adafruit_ADS1x15.Adafruit_ADS1x15 import ADS1x15
import time

pga = 1024
sps = 32
adc = ADS1x15(address=0x48, ic=0x01)

a1 = adc.readADCDifferential01(pga, sps)
time.sleep(0.01)
a2 = adc.readADCDifferential23(pga, sps)

ratio = a1/a2

print a1
print a2
print ratio
