import os
import sys
import threading
import serial

sys.path.insert(0, "modules/")

mods = []
arduino = None
metrics = {}
errors = {}
kErrors = {}
modsDir = os.listdir("modules/")

#Send Arduino Message        
def sendArduinoMessage(mssg):
    arduino.write(mssg)
    
#Connect to an Arduino board    
def connectToArduino(dev, rate):
    arduino = serial.Serial(dev, rate)
    
    while True:
        strIn = arduino.readline()
        for mod in mods:
            if strIn.beginswith("(" + mod.moduleName() + ")"):
                mod.incomingArduinoMessage(strIn.replace("(" + mod.moduleName() + ")", ""))

#Add a metric                
def addMetric(key, value, mod):
    metrics[mod + "." + key] = value;

#Get a metric    
def getMetric(key, mod):
    return metrics[mod + "." + key];
    
#Report an error    
def sendError(error, level, mod):
    errors[mod + "." + error] = level
    if level == kErrors["eCritical"]:
        pass
    
#Sends an SMS to the specified recipiant
def sendSMS(mssg, recipiant):
    pass
    
#Sends an SMS to the specified recipiant
def checkForIncomingSMS():
    pass
    
#Configure error levels
kErrors["eWarning"] = 0
kErrors["eStandard"] = 1
kErrors["eCritical"] = 2

#Load all other modules
for mod in modsDir:
    if mod != ".DS_Store" and ".pyc" not in mod:
        _mod = __import__(mod.replace(".py", ""))
        
        if getattr(_mod, 'moduleInit', None) is None or getattr(_mod, 'moduleRun', None) is None or getattr(_mod, 'moduleVersion', None) is None or getattr(_mod, 'moduleAuthor', None) is None or getattr(_mod, 'incomingArduinoMessage', None) is None or getattr(_mod, 'moduleDescription', None) is None or getattr(_mod, 'moduleName', None) is None or getattr(_mod, 'stopModule', None) is None:
            print "Error loading module: " + mod + ". The module is not configured correctly."
        else:
            try:
                print "Loaded " + mod.replace(".py", "")  + ", version " + _mod.moduleVersion() + " by " +  _mod.moduleAuthor()
            except:
                print sys.exc_info()[0]
                sendError("Access on Version or Author failure", kErrors["eStandard"], mod.replace(".py", ""))
            
            try:
                _mod.moduleInit(addMetric, getMetric, sendError, sendArduinoMessage, kErrors)
            except:
                sendError("Init():" + sys.exc_info()[0], kErrors["eCritical"], mod.replace(".py", ""))
            
            try:
                modThread = threading.Thread(target=_mod.moduleRun())
                modThread.start()
            except:
                sendError("Run():" + sys.exc_info()[0], kErrors["eCritical"], mod.replace(".py", ""))
            
            mods.append(_mod)

smsThread = threading.Thread(target=checkForIncomingSMS)
smsThread.start()

#Connect to the Arduino board on a seperate thread
arduinoThread = threading.Thread(target=connectToArduino("/dev/tty.usbserial-A6027N04", 9600))
arduinoThread.start()

while True:
    cmd = raw_input("FishTank$ ")
    if cmd == "exit":
        for mod in mods:
            mod.stopModule()
        sys.exit(0)
    elif cmd == "metrics":
        print metrics
    elif cmd == "errors":
        print errors
    else:
       print "Unrecognized command"