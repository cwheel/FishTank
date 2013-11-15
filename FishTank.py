import os
import sys
import thread
import serial
import threading
import base64
import imaplib
import smtplib
import getpass
import Queue
import re
import time
import BaseHTTPServer

sys.path.insert(0, "modules/")

mods = []
smsRecipients = []
arduino = None
arduinoDevice = None
mode = None
metrics = {}
smsCmds = {}
errors = {}
kErrors = {}
modsDir = os.listdir("modules/")
mailPass = None
webUI = None;
exitInProcess = False
printQueue = Queue.Queue()
writeQueue = Queue.Queue()

#Send Arduino Message        
def sendArduinoMessage(module, mssg):
    writeQueue.put(base64.b64encode("(" + module + "):" + mssg))
    
#Connect to an Arduino board    
def connectToArduino():
    while True and not exitInProcess:
        try:
            strIn = base64.b64decode(arduino.readline())
            
            for mod in mods:
                if strIn.startswith("(" + mod.moduleName() + ")"):
                    mod.incomingQueue.put(strIn.replace("(" + mod.moduleName() + "):", ""))
        except:
            log("FishTank Core", str(sys.exc_info()[0]))
            
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
        if mode != "--nosms":
            for recip in smsRecipients:
                sendSMS(mod + "." + error, recip)
            
    
#Sends an SMS to the specified recipiant
def sendSMS(mssg, recipiants):
    if mode != "--nosms":
        mailserver = smtplib.SMTP('smtp.gmail.com', 587)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.login("fishtanksms@gmail.com", mailPass)
       
        mailserver.sendmail("fishtanksms@gmail.com", recipiants, mssg)
        mailserver.quit()
    
#Reads from the incoming IMAP server
def checkForIncomingSMS():
    if mode != "--nosms":
        while True:
            mailserver = imaplib.IMAP4_SSL("imap.gmail.com", 993)
            mailserver.login("fishtanksms@gmail.com", mailPass)
            mailserver.select('INBOX')
            stat, ids = mailserver.uid('search', None, "UnSeen")
            
            if "['']" not in str(ids):
                for id in ids[0].split(" "):
                    result, email = mailserver.uid('fetch', id, '(RFC822)')
                    sender = re.compile("From:.*").search(email[0][1]).group().replace("From:", "")
                    
                    if "saltyfish" in email[0][1] or "Saltyfish" in email[0][1]:
                        if not sender in smsRecipients:
                            sendSMS("You've subscribed to the FishTank. To unsubscribe, reply 'remove'.", [sender])
                            smsRecipients.append(sender)
                            saveRecipients()
                            
                    elif "remove" in email[0][1] or "Remove" in email[0][1]:
                        sendSMS("You've unsubscribed from the FishTank.", [sender])
                        smsRecipients.remove(sender)
                        saveRecipients()
                        
                    elif "modules" in email[0][1] or "Modules" in email[0][1] or "mods" in email[0][1] or "Mods" in email[0][1]:
                        if sender in smsRecipients:
                            sendSMS("Active Modules: \n" + mods, [sender])
                            
                    elif "errors" in email[0][1] or "Errors" in email[0][1]:
                        if sender in smsRecipients:
                            sendSMS("Reported Errors: \n" + errors, [sender])
                            
                    elif "metrics" in email[0][1] or "Metrics" in email[0][1]:
                        if sender in smsRecipients:
                            sendSMS("Metrics: \n" + metrics, [sender])
                    else:
                        if sender in smsRecipients:
                            for cmd in smsCmds:
                                if cmd in email[0][1] or cmd.title() in email[0][1] :
                                    mssg = smsCmds[cmd]()
                                    if mssg != None:
                                        sendSMS(mssg, [sender])
                            
                                            
            time.sleep(360)

#Registers an SMS command
def registerSMSCommand(cmd, func):
         smsCmds[cmd] = func
         
#Write out any queued messages for Arduino     
def writeQueueToBoard():
    try:
        while True:
            i = 0
            while i < writeQueue.qsize():
                arduino.write(writeQueue.get())
                writeQueue.task_done()
    except:
        log("FishTank Core", str(sys.exc_info()[0]))
            
#Save the SMS recipients list
def saveRecipients():
    if not os.path.exists("sms_subscribers"):
        f = open("sms_subscribers", "a+")
    else:
        f = open("sms_subscribers", "w")

    f.writelines(smsRecipients)
    f.close()

def runWebserver():
    webUI.serve_forever()

class WebUIHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_GET(self):
        try:
            if "./" not in self.path:
                if self.path.endswith('.html'):
                    f = open("webui/" + self.path)
                    self.send_response(200)
                    self.send_header('Content-type', "text/html")
                    self.end_headers()
                    
                    file = f.read()
                    
                    if "errors.html" in self.path:
                        for err in errors.keys():
                            level = None
                            if errors[err] == kErrors["eWarning"]:
                                level = "Warning"
                            elif errors[err] == kErrors["eStandard"]:
                                level = "Standard"
                            elif errors[err] == kErrors["eCritical"]: 
                                level = "<b>Critical</b>"
                            
                            file = file + "\n<tr><td>" + err.split(".")[0] +"</td><td>" + level + "</td><td>" + err.split(".")[1] + "</tr>"
                        
                        
                    elif "metrics.html" in self.path:
                        for metric in metrics.keys():
                            file = file + "\n<tr><td>" + metric.split(".")[0] +"</td><td>" + metric.split(".")[1] + "</td><td>" + metrics[metric] + "</tr>"
                        
                    self.wfile.write(file)
                    f.close()
                    return
                    
                elif self.path.endswith('.css'):
                    f = open("webui/" + self.path)
                    self.send_response(200)
                    self.send_header('Content-type', "text/css")
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return
                    
                elif self.path.endswith('.png'):
                    f = open("webui/" + self.path)
                    self.send_response(200)
                    self.send_header('Content-type', "image/png")
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return
                    
                elif "." not in self.path:
                    f = open("webui/webui.html")
                    self.send_response(200)
                    self.send_header('Content-type', "text/html")
                    self.end_headers()
                    
                    file = f.read()
                    
                    for mod in mods:
                        file = file + "\n<tr><td>" + mod.moduleName() +"</td><td>" + mod.moduleVersion() + "</td><td>" + mod.moduleAuthor() + "</td><td>" + mod.moduleDescription() +"</td></tr>"
                    
                    self.wfile.write(file)
                    f.close()
                    return
                    
                else:
                    self.send_error(404, 'File not found')
            else:
                self.send_error(403, 'Forbidden')
            
        except IOError:
            self.send_error(404, 'File not found')
            
    def log_message(self, format, *args):
            return
            
#Configure error levels
kErrors["eWarning"] = 0
kErrors["eStandard"] = 1
kErrors["eCritical"] = 2

#Set the mode

try:
    mode = sys.argv[1]
except:
    mode = ""

#Get mail information
while mailPass == "" or mailPass == " " or mailPass == None and mode != "--nosms":
    mailPass = getpass.getpass("Mail (SMS) Password:")
    
#Load subscribers

if os.path.exists("sms_subscribers"):
    f = open("sms_subscribers", "r")
    for subscriber in f:
        if subscriber != "" or subscriber != " ":
            smsRecipients.append(subscriber)

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
                _mod.moduleInit(addMetric, getMetric, sendError, sendArduinoMessage, log, registerSMSCommand, kErrors)
            except:
                sendError("Init():" + str(sys.exc_info()[0]), kErrors["eCritical"], mod.replace(".py", ""))
            
            try:
                thread.start_new_thread(_mod.moduleRun, (addMetric, getMetric, sendError, sendArduinoMessage, log, registerSMSCommand, kErrors))
            except:
                sendError("Run():" + str(sys.exc_info()[0]), kErrors["eCritical"], mod.replace(".py", ""))
            
            mods.append(_mod)
            
webUI = BaseHTTPServer.HTTPServer(('', 8080), WebUIHandler)
thread.start_new_thread(checkForIncomingSMS, ())
thread.start_new_thread(writeQueueToBoard, ())
thread.start_new_thread(runWebserver, ())

#arduino = serial.Serial("/dev/tty.usbserial-A6027N04", 9600)
thread.start_new_thread(connectToArduino, ())
#sendArduinoMessage("hola", "hi")

#Run loop for CLI
print "\n"
while True:
    cmd = raw_input("FishTank$ ")
    if cmd == "exit":
        exitInProcess =  True
        webUI.socket.close()
        
        for mod in mods:
            mod.stopModule(log)
        
        try:    
            arduino.close()
        except:
            print "Could not disconnect Arduino. Perhaps one was never connected..."
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
            arduino = serial.Serial(arduinoDevice, 9600)
            thread.start_new_thread(connectToArduino, ())
    elif "stop" in cmd:
        for mod in mods:
            if mod.moduleName() == cmd.replace("stop ", ""):
                mod.stopModule(log)
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