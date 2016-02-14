from Adafruit.Adafruit_ADS1x15.Adafruit_ADS1x15 import ADS1x15
pga = 6144
sps = 8
adc = ADS1x15(ic=0x01)
print adc.readADCDifferential01(pga, sps)
