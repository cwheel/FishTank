import os
import sys
import thread
import serial
import threading
import base64
import imaplib
import getpass
import Queue
import re

sys.path.insert(0, "modules/")

mods = []
arduino = None
arduinoDevice = None
metrics = {}
errors = {}
kErrors = {}
modsDir = os.listdir("modules/")
mailPass = None
printQueue = Queue.Queue()
writeQueue = Queue.Queue()

##TODO##
#Finish SMS implimentation
#Fix the log() function

#Send Arduino Message        
def sendArduinoMessage(mssg):
    writeQueue.put(base64.b64encode(mssg))
    
#Connect to an Arduino board    
def connectToArduino(dev, rate):
    arduino = serial.Serial(dev, rate)
    
    while True:
        strIn = base64.b64decode(arduino.readline())
        for mod in mods:
            if strIn.beginswith("(" + mod.moduleName() + ")"):
                mod.incomingQueue.put(strIn.replace("(" + mod.moduleName() + ")", ""))

#Add a metric                
def addMetric(key, value, mod):
    metrics[mod + "." + key] = value;

#Get a metric    
def getMetric(key, mod):
    return metrics[mod + "." + key];
    
#Logging for modules             
def log(mod, mssg):
    printQueue.put("[" + mod + "] "+ mssg)
    
#Report an error    
def sendError(error, level, mod):
    errors[mod + "." + error] = level
    if level == kErrors["eCritical"]:
        sendSMS(mod + "." + error, "")
    
#Sends an SMS to the specified recipiant
def sendSMS(mssg, recipiant):
    pass
    
#Reads from the incoming IMAP server
def checkForIncomingSMS():
     mailserver = imaplib.IMAP4_SSL("imap.gmail.com", 993)
     mailserver.login("fishtank@nosedivesoftware.com", mailPass)
     mailserver.select('INBOX')
     stat, ids = mailserver.uid('search', None, "ALL")
     for id in ids[0].split(" "):
        result, email = mailserver.uid('fetch', id, '(RFC822)')
        if "saltyfish" in email[0][1]:
            sender = re.compile("From: .*").search(email[0][1]).group()[0]
            print sender
     
#Write out any queued messages for Arduino     
def writeQueueToBoard():
    while True:
        i = 0
        while i < writeQueue.qsize():
            arduino.write(writeQueue.get())
            writeQueue.task_done()
    
#Configure error levels
kErrors["eWarning"] = 0
kErrors["eStandard"] = 1
kErrors["eCritical"] = 2

#Get mail information

while mailPass == "" or mailPass == " " or mailPass == None:
    mailPass = getpass.getpass("Mail Password:")

#Load all other modules
for mod in modsDir:
    if mod != ".DS_Store" and ".pyc" not in mod:
        _mod = __import__(mod.replace(".py", ""))
        
        if getattr(_mod, 'moduleInit', None) is None or getattr(_mod, 'moduleRun', None) is None or getattr(_mod, 'moduleVersion', None) is None or getattr(_mod, 'moduleAuthor', None) is None or getattr(_mod, 'moduleDescription', None) is None or getattr(_mod, 'moduleName', None) is None or getattr(_mod, 'stopModule', None) is None:
            print "Error loading module: " + mod + ". The module is not configured correctly."
        else:
            try:
                print "Loaded " + mod.replace(".py", "")  + ", version " + _mod.moduleVersion() + " by " +  _mod.moduleAuthor()
            except:
                print sys.exc_info()[0]
                sendError("Access on Version or Author failure", kErrors["eStandard"], mod.replace(".py", ""))
            
            try:
                _mod.moduleInit(addMetric, getMetric, sendError, sendArduinoMessage, log, kErrors)
            except:
                sendError("Init():" + str(sys.exc_info()[0]), kErrors["eCritical"], mod.replace(".py", ""))
            
            try:
                thread.start_new_thread(_mod.moduleRun, (addMetric, getMetric, sendError, sendArduinoMessage, log, kErrors))
            except:
                sendError("Run():" + str(sys.exc_info()[0]), kErrors["eCritical"], mod.replace(".py", ""))
            
            mods.append(_mod)

thread.start_new_thread(checkForIncomingSMS, ())
thread.start_new_thread(writeQueueToBoard, ())

#Run loop for CLI
print "\n"
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
    elif "set" in cmd:
        if "arduino" in cmd:
            arduinoDevice = cmd.replace("set arduino ", "")
        else:
            print "set: Invalid variable name"
    elif cmd == "mods" or cmd == "modules":
        for mod in mods:
            print mod.moduleName()
    elif "connect" in cmd:
        if "arduino" in cmd and not arduinoDevice == None:
            thread.start_new_thread(connectToArduino, (arduinoDevice, 9600))
    elif "stop" in cmd:
        for mod in mods:
            if mod.moduleName() == cmd.replace("stop ", ""):
                mod.stopModule()
    elif cmd == "help":
        print "FishTank Help"
        print "============="
        print "metrics: displays the avalible metrics from loaded modules"
        print "errors: displays any reported errors from loaded modules"
        print "stop <module name>: stops the specified module"
        print "set <var name> <value>: sets the given variable to the specified value"
        print "connect <device name>: initiates a connection to the specified device"
        print "list <devices | variables>: lists the avalible devices or variables"
        print "exit: requests that all modules stop and quits FishTank"
    elif "list" in cmd:
        if "devices" in cmd:
            if not arduinoDevice == None:
                print "'arduino': " + arduinoDevice
        elif "variables" in cmd:
            if arduinoDevice == None:
                print "arduino: not set"
            else:
                 print "arduino: " + arduinoDevice
        else:
            print "list: Invalid item to list"
    elif cmd == "log":
        i = 0
        while i < printQueue.qsize():
            print printQueue.get()
            printQueue.task_done()
    else:
       print "Unrecognized command"