from fianium import *

fia = FianiumLaser()
fia.enable()
fia.ask("O") #find out if it's ready to run yet.
fia.setOutputRepetitionRate(0.01)
fia.setOutputAmplitude(25) #low power here: doesn't seem to be linear. Threshold?
#fia.setAmplifierControlValue(1) #minimum power please
fia.setAmplifierControlValue(0) #minimum power please

fia.getPulseEnergy() #this returns an error, because it only works for very specific internal control values

a=self.getAmplifierControlValue()
cv=a[11:14]
out_amp=self.getOutputAmplitude()
